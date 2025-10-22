# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.

# Keep model classes for Gson
-keepclassmembers class com.voicedictation.provider.** { *; }

# Keep Retrofit interfaces
-keep interface com.voicedictation.provider.** { *; }

# OkHttp platform
-dontwarn okhttp3.internal.platform.**
-dontwarn org.conscrypt.**
-dontwarn org.bouncycastle.**
-dontwarn org.openjsse.**

# Timber
-dontwarn org.jetbrains.annotations.**

# Kotlin Coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}

# Accessibility Service
-keep class * extends android.accessibilityservice.AccessibilityService

# Keep native methods
-keepclasseswithmembernames class * {
    native <methods>;
}
