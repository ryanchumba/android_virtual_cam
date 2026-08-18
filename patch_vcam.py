import re
import os

target_file = "app/src/main/java/com/example/vcam/HookMain.java"

if not os.path.exists(target_file):
    print("[-] Error: Could not find HookMain.java in current directory.")
    exit(1)

with open(target_file, "r") as f:
    code = f.read()

# 1. Add ImageFormat import
if "import android.graphics.ImageFormat;" not in code:
    code = code.replace(
        "import android.graphics.Bitmap;",
        "import android.graphics.Bitmap;\nimport android.graphics.ImageFormat;"
    )

# 2. Inject Process Check & ImageReader Hook
process_guard_and_hook = '''
        if (!lpparam.packageName.equals("money.nala.remit")) {
            return;
        }
        if (!lpparam.processName.equals(lpparam.packageName)) {
            return;
        }

        XposedHelpers.findAndHookMethod(
            "android.media.ImageReader",
            lpparam.classLoader,
            "newInstance",
            int.class, int.class, int.class, int.class,
            new de.robv.android.xposed.XC_MethodHook() {
                @Override
                protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
                    int requestedFormat = (int) param.args[2];
                    if (requestedFormat != ImageFormat.JPEG) {
                        param.args[2] = ImageFormat.YUV_420_888;
                    }
                }
            }
        );
'''

if "money.nala.remit" not in code:
    target_pattern = r"(public void handleLoadPackage\(XC_LoadPackage\.LoadPackageParam lpparam\) throws Throwable \{)"
    code = re.sub(target_pattern, r"\1\n" + process_guard_and_hook, code)

with open(target_file, "w") as f:
    f.write(code)

print("[✓] Patch successfully applied to HookMain.java!")
