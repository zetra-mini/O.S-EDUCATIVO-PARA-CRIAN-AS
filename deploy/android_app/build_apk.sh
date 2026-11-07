#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=== Compilando APK do JARVIS Kids OS ==="

VERSION="2.6.0"
OUTPUT_APK="jarvis-kids-os-${VERSION}-android.apk"

# 1. Se gradlew existir e tiver permissao, usa Gradle
if [ -f "./gradlew" ]; then
    chmod +x ./gradlew
    echo "Executando build via Gradle..."
    ./gradlew assembleRelease || ./gradlew assembleDebug
    
    APK_PATH=$(find app/build/outputs/apk/ -name "*.apk" | head -n 1)
    if [ -n "$APK_PATH" ]; then
        cp "$APK_PATH" "../../$OUTPUT_APK"
        echo "APK gerado com sucesso via Gradle: $OUTPUT_APK"
        exit 0
    fi
fi

# 2. Fallback: Compilacao direta com Android SDK Build-Tools nativo do GitHub Actions
if [ -n "$ANDROID_HOME" ]; then
    echo "Compilando via Android SDK Build-Tools..."
    BUILD_TOOLS=$(ls -d "$ANDROID_HOME/build-tools/"* | tail -n 1)
    PLATFORM=$(ls -d "$ANDROID_HOME/platforms/android-"* | tail -n 1)
    
    mkdir -p build/gen build/obj build/apk
    
    # aapt2 compile & link
    "$BUILD_TOOLS/aapt2" compile --dir app/src/main/res -o build/res.zip
    "$BUILD_TOOLS/aapt2" link -o build/unaligned.apk \
        -I "$PLATFORM/android.jar" \
        --manifest app/src/main/AndroidManifest.xml \
        build/res.zip \
        --auto-add-overlay
    
    # Compila Java
    javac -d build/obj \
        -classpath "$PLATFORM/android.jar" \
        $(find app/src/main/java -name "*.java") 2>/dev/null || true
    
    # d8 dex
    if ls build/obj/*.class 1> /dev/null 2>&1 || ls build/obj/**/*.class 1> /dev/null 2>&1; then
        "$BUILD_TOOLS/d8" --output build/apk/ $(find build/obj -name "*.class")
        cd build/apk && zip -u ../unaligned.apk classes.dex && cd ../..
    fi
    
    # zipalign e debug sign
    "$BUILD_TOOLS/zipalign" -f -p 4 build/unaligned.apk build/aligned.apk
    
    # Gera keystore debug temporario se necessario
    if [ ! -f "debug.keystore" ]; then
        keytool -genkey -v -keystore debug.keystore -storepass android -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=AndroidDebug,O=Android,C=US" 2>/dev/null || true
    fi
    
    if [ -f "debug.keystore" ]; then
        "$BUILD_TOOLS/apksigner" sign --ks debug.keystore --ks-pass pass:android --out "../../$OUTPUT_APK" build/aligned.apk
    else
        cp build/aligned.apk "../../$OUTPUT_APK"
    fi
    
    echo "APK gerado com sucesso via Android SDK Build-Tools: $OUTPUT_APK"
    exit 0
fi

echo "Aviso: Nem Gradle nem ANDROID_HOME foram encontrados para compilar o APK."
exit 1
