using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using BepInEx;
using BepInEx.Logging;
using BepInEx.Unity.IL2CPP;
using HarmonyLib;
using Il2CppInterop.Runtime;

namespace SableItalianMod;

[BepInPlugin(GUID, "Sable Italian Translation", "0.1.0")]
public class Plugin : BasePlugin
{
    public const string GUID = "com.sam4000133.sable-italian";

    internal static new ManualLogSource Log;
    internal static Dictionary<string, string> ItStrings = new();

    // canonical item Name -> (Name_IT, Description_IT, ShopDescription_IT)
    internal static Dictionary<string, (string Name, string Desc, string ShopDesc)> ItItems = new();

    // Italian Ink JSON content (full sable.bin replacement)
    internal static string ItInkJson;

    public override void Load()
    {
        Log = base.Log;
        Log.LogInfo("Sable Italian Mod starting...");

        LoadTranslations();
        LoadItemTranslations();
        LoadInkTranslation();
        Log.LogInfo($"Loaded {ItStrings.Count} UI strings, {ItItems.Count} item translations, ink IT bytes: {ItInkJson?.Length ?? 0}");

        var harmony = new Harmony(GUID);
        PatchTextProviderEN(harmony);
        PatchLocalisedText(harmony);
        PatchItemDefinition(harmony);
        PatchTextAssetGetText(harmony);
        Log.LogInfo("Sable Italian Mod ready.");
    }

    private void LoadTranslations()
    {
        // CSV next to the plugin DLL
        string pluginPath = Path.GetDirectoryName(typeof(Plugin).Assembly.Location);
        string csv = Path.Combine(pluginPath, "it_strings.csv");
        if (!File.Exists(csv))
        {
            Log.LogError($"Translation file not found at {csv}");
            return;
        }
        bool first = true;
        foreach (var line in File.ReadAllLines(csv))
        {
            if (first) { first = false; continue; }
            // naive CSV parse: 3 cols, last unquoted field may include commas — but ours don't
            var parts = SplitCsv(line);
            if (parts.Count < 3) continue;
            ItStrings[parts[0]] = parts[2];
        }
    }

    private void LoadInkTranslation()
    {
        string pluginPath = Path.GetDirectoryName(typeof(Plugin).Assembly.Location);
        string inkFile = Path.Combine(pluginPath, "sable_it.bin");
        if (!File.Exists(inkFile))
        {
            Log.LogWarning($"Italian Ink file not found at {inkFile}");
            return;
        }
        try
        {
            ItInkJson = File.ReadAllText(inkFile);
            // Strip leading BOM if present (Unity TextAsset.text returns without BOM)
            if (ItInkJson.Length > 0 && ItInkJson[0] == '﻿') ItInkJson = ItInkJson.Substring(1);
        }
        catch (Exception e)
        {
            Log.LogError($"Failed to read sable_it.bin: {e.Message}");
        }
    }

    private void LoadItemTranslations()
    {
        string pluginPath = Path.GetDirectoryName(typeof(Plugin).Assembly.Location);
        string csv = Path.Combine(pluginPath, "it_items.csv");
        if (!File.Exists(csv))
        {
            Log.LogWarning($"Item translation file not found at {csv}");
            return;
        }
        bool first = true;
        foreach (var line in File.ReadAllLines(csv))
        {
            if (first) { first = false; continue; }
            var parts = SplitCsv(line);
            // Expected cols: Name, Name_IT, Description_IT, ShopDescription_IT
            if (parts.Count < 4) continue;
            var name = parts[0];
            if (string.IsNullOrEmpty(name)) continue;
            ItItems[name] = (parts[1], parts[2], parts[3]);
        }
    }

    private static List<string> SplitCsv(string line)
    {
        var result = new List<string>();
        var cur = new System.Text.StringBuilder();
        bool inQuotes = false;
        foreach (var c in line)
        {
            if (c == '"') { inQuotes = !inQuotes; continue; }
            if (c == ',' && !inQuotes) { result.Add(cur.ToString()); cur.Clear(); continue; }
            cur.Append(c);
        }
        result.Add(cur.ToString());
        return result;
    }

    private void PatchTextProviderEN(Harmony harmony)
    {
        // First try already-loaded assemblies
        Type textProviderEn = null;
        foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
        {
            textProviderEn = asm.GetType("TextProviders.Implementations.TextProvider_EN");
            if (textProviderEn != null)
            {
                Log.LogInfo($"Found TextProvider_EN in already-loaded {asm.GetName().Name}");
                break;
            }
        }
        if (textProviderEn == null)
        {
            // Explicitly load the interop Assembly-CSharp.dll
            string pluginPath = Path.GetDirectoryName(typeof(Plugin).Assembly.Location);
            string interopDll = Path.GetFullPath(Path.Combine(pluginPath, "..", "..", "interop", "Assembly-CSharp.dll"));
            Log.LogInfo($"Loading interop assembly from {interopDll}");
            try
            {
                var loaded = Assembly.LoadFrom(interopDll);
                textProviderEn = loaded.GetType("TextProviders.Implementations.TextProvider_EN");
                if (textProviderEn != null)
                    Log.LogInfo($"Found TextProvider_EN after loading {loaded.GetName().Name}");
            }
            catch (Exception e)
            {
                Log.LogError($"Failed to load interop Assembly-CSharp.dll: {e.Message}");
            }
        }
        if (textProviderEn == null)
        {
            Log.LogError("Could not find TextProviders.Implementations.TextProvider_EN type");
            return;
        }
        Log.LogInfo($"Type: {textProviderEn.AssemblyQualifiedName}");

        // Postfix all string-returning property getters
        var postfix = new HarmonyMethod(typeof(Plugin).GetMethod(nameof(GetterPostfix), BindingFlags.NonPublic | BindingFlags.Static));
        int patched = 0;
        foreach (var method in textProviderEn.GetMethods(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic))
        {
            if (!method.Name.StartsWith("get_")) continue;
            if (method.ReturnType != typeof(string)) continue;
            if (method.GetParameters().Length != 0) continue;
            try
            {
                harmony.Patch(method, postfix: postfix);
                patched++;
            }
            catch (Exception e)
            {
                Log.LogWarning($"Failed to patch {method.Name}: {e.Message}");
            }
        }
        Log.LogInfo($"Patched {patched} TextProvider_EN getters.");
    }

    private static void GetterPostfix(MethodBase __originalMethod, ref string __result)
    {
        var name = __originalMethod.Name;
        if (!name.StartsWith("get_")) return;
        var key = name.Substring(4);
        if (ItStrings.TryGetValue(key, out var it) && !string.IsNullOrEmpty(it))
        {
            __result = it;
        }
    }

    private static Type _localisedTextType;
    private static PropertyInfo _localisedTextKeyProp;
    private static PropertyInfo _localisedTextTmpProp;
    private static PropertyInfo _tmpTextProp;

    private void PatchLocalisedText(Harmony harmony)
    {
        Type localisedText = null;
        // Try loaded assemblies, then explicit interop load
        foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
        {
            localisedText = asm.GetType("LocalisedText");
            if (localisedText != null) break;
        }
        if (localisedText == null)
        {
            string pluginPath = Path.GetDirectoryName(typeof(Plugin).Assembly.Location);
            string interopDll = Path.GetFullPath(Path.Combine(pluginPath, "..", "..", "interop", "Assembly-CSharp.dll"));
            try
            {
                var loaded = Assembly.LoadFrom(interopDll);
                localisedText = loaded.GetType("LocalisedText");
            }
            catch (Exception e) { Log.LogError($"Load fail: {e.Message}"); }
        }
        if (localisedText == null)
        {
            Log.LogError("Could not find LocalisedText type");
            return;
        }
        _localisedTextType = localisedText;
        const BindingFlags allInst = BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public;
        _localisedTextKeyProp = localisedText.GetProperty("LocalisationKey", allInst);
        _localisedTextTmpProp = localisedText.GetProperty("_text", allInst);
        Log.LogInfo($"LocalisedText: keyProp={_localisedTextKeyProp != null}, tmpProp={_localisedTextTmpProp != null}");

        var update = localisedText.GetMethod("UpdateText", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);
        if (update == null)
        {
            Log.LogError("Could not find LocalisedText.UpdateText method");
            return;
        }
        var postfix = new HarmonyMethod(typeof(Plugin).GetMethod(nameof(UpdateTextPostfix), BindingFlags.NonPublic | BindingFlags.Static));
        try
        {
            harmony.Patch(update, postfix: postfix);
            Log.LogInfo("Patched LocalisedText.UpdateText");
        }
        catch (Exception e)
        {
            Log.LogError($"Failed to patch UpdateText: {e.Message}");
        }
    }

    private static bool _loggedFirstHit;
    private static PropertyInfo _itemDefNameProp;

    private void PatchItemDefinition(Harmony harmony)
    {
        Type itemDef = null;
        foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
        {
            itemDef = asm.GetType("ItemDefinition");
            if (itemDef != null) break;
        }
        if (itemDef == null)
        {
            Log.LogError("Could not find ItemDefinition type");
            return;
        }
        const BindingFlags allInst = BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public;
        // Il2CppInterop exposes the canonical Name field as a property
        _itemDefNameProp = itemDef.GetProperty("Name", allInst);
        if (_itemDefNameProp == null)
        {
            Log.LogError("ItemDefinition.Name property not found");
            return;
        }

        var nameMethod = itemDef.GetMethod("GetName", allInst);
        var descMethod = itemDef.GetMethod("GetDescription", allInst);
        var shopMethod = itemDef.GetMethod("GetShopDescription", allInst);
        Log.LogInfo($"ItemDefinition methods: GetName={nameMethod != null}, GetDescription={descMethod != null}, GetShopDescription={shopMethod != null}");

        var pName = new HarmonyMethod(typeof(Plugin).GetMethod(nameof(GetNamePostfix), BindingFlags.NonPublic | BindingFlags.Static));
        var pDesc = new HarmonyMethod(typeof(Plugin).GetMethod(nameof(GetDescriptionPostfix), BindingFlags.NonPublic | BindingFlags.Static));
        var pShop = new HarmonyMethod(typeof(Plugin).GetMethod(nameof(GetShopDescriptionPostfix), BindingFlags.NonPublic | BindingFlags.Static));

        try { harmony.Patch(nameMethod, postfix: pName); Log.LogInfo("Patched ItemDefinition.GetName"); } catch (Exception e) { Log.LogError($"GetName patch fail: {e.Message}"); }
        try { harmony.Patch(descMethod, postfix: pDesc); Log.LogInfo("Patched ItemDefinition.GetDescription"); } catch (Exception e) { Log.LogError($"GetDescription patch fail: {e.Message}"); }
        try { harmony.Patch(shopMethod, postfix: pShop); Log.LogInfo("Patched ItemDefinition.GetShopDescription"); } catch (Exception e) { Log.LogError($"GetShopDescription patch fail: {e.Message}"); }
    }

    private static string GetCanonicalItemName(object instance)
    {
        if (_itemDefNameProp == null || instance == null) return null;
        try { return _itemDefNameProp.GetValue(instance) as string; }
        catch { return null; }
    }

    private static void GetNamePostfix(object __instance, ref string __result)
    {
        var n = GetCanonicalItemName(__instance);
        if (n != null && ItItems.TryGetValue(n, out var v) && !string.IsNullOrEmpty(v.Name))
            __result = v.Name;
    }
    private static void GetDescriptionPostfix(object __instance, ref string __result)
    {
        var n = GetCanonicalItemName(__instance);
        if (n != null && ItItems.TryGetValue(n, out var v) && !string.IsNullOrEmpty(v.Desc))
            __result = v.Desc;
    }
    private static void GetShopDescriptionPostfix(object __instance, ref string __result)
    {
        var n = GetCanonicalItemName(__instance);
        if (n != null && ItItems.TryGetValue(n, out var v) && !string.IsNullOrEmpty(v.ShopDesc))
            __result = v.ShopDesc;
    }

    private static void UpdateTextPostfix(object __instance)
    {
        try
        {
            if (_localisedTextKeyProp == null || _localisedTextTmpProp == null) return;
            var key = _localisedTextKeyProp.GetValue(__instance) as string;
            if (string.IsNullOrEmpty(key)) return;
            if (!ItStrings.TryGetValue(key, out var it) || string.IsNullOrEmpty(it)) return;

            var tmp = _localisedTextTmpProp.GetValue(__instance);
            if (tmp == null) return;
            if (_tmpTextProp == null)
            {
                Type t = tmp.GetType();
                while (t != null && _tmpTextProp == null)
                {
                    _tmpTextProp = t.GetProperty("text", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
                    t = t.BaseType;
                }
                if (_tmpTextProp == null) { Log.LogWarning($"text property not found on {tmp.GetType()}"); return; }
            }
            _tmpTextProp.SetValue(tmp, it);
            if (!_loggedFirstHit)
            {
                _loggedFirstHit = true;
                Log.LogInfo($"First IT-translation applied: '{key}' -> '{it}'");
            }
        }
        catch (Exception e)
        {
            Log.LogWarning($"UpdateTextPostfix error for: {e.Message}");
        }
    }

    private static PropertyInfo _textAssetNameProp;
    private static bool _loggedFirstInkHit;

    private void PatchTextAssetGetText(Harmony harmony)
    {
        if (string.IsNullOrEmpty(ItInkJson))
        {
            Log.LogWarning("No Italian Ink JSON loaded — skipping TextAsset hook");
            return;
        }
        Type textAsset = null;
        foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
        {
            textAsset = asm.GetType("UnityEngine.TextAsset");
            if (textAsset != null) break;
        }
        if (textAsset == null)
        {
            string pluginPath = Path.GetDirectoryName(typeof(Plugin).Assembly.Location);
            string interopDir = Path.GetFullPath(Path.Combine(pluginPath, "..", "..", "interop"));
            foreach (var dll in Directory.GetFiles(interopDir, "UnityEngine*.dll"))
            {
                try
                {
                    var asm = Assembly.LoadFrom(dll);
                    textAsset = asm.GetType("UnityEngine.TextAsset");
                    if (textAsset != null) break;
                }
                catch { }
            }
        }
        if (textAsset == null) { Log.LogError("UnityEngine.TextAsset type not found"); return; }
        Log.LogInfo($"TextAsset type: {textAsset.AssemblyQualifiedName}");

        const BindingFlags allInst = BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public;
        var textProp = textAsset.GetProperty("text", allInst);
        if (textProp == null) { Log.LogError("TextAsset.text property not found"); return; }
        var getText = textProp.GetGetMethod(true);
        if (getText == null) { Log.LogError("TextAsset.text getter missing"); return; }

        _textAssetNameProp = textAsset.GetProperty("name", allInst);
        Log.LogInfo($"TextAsset.name property: {_textAssetNameProp != null}");

        var postfix = new HarmonyMethod(typeof(Plugin).GetMethod(nameof(TextAssetGetTextPostfix), BindingFlags.NonPublic | BindingFlags.Static));
        try
        {
            harmony.Patch(getText, postfix: postfix);
            Log.LogInfo("Patched UnityEngine.TextAsset.get_text");
        }
        catch (Exception e)
        {
            Log.LogError($"Failed to patch TextAsset.get_text: {e.Message}");
        }
    }

    private static void TextAssetGetTextPostfix(object __instance, ref string __result)
    {
        try
        {
            if (string.IsNullOrEmpty(ItInkJson) || _textAssetNameProp == null || __instance == null) return;
            var name = _textAssetNameProp.GetValue(__instance) as string;
            if (name != "sable") return;
            __result = ItInkJson;
            if (!_loggedFirstInkHit)
            {
                _loggedFirstInkHit = true;
                Log.LogInfo($"First Ink IT served — name='{name}', length={ItInkJson.Length}");
            }
        }
        catch (Exception e) { Log.LogWarning($"TextAssetGetTextPostfix err: {e.Message}"); }
    }
}
