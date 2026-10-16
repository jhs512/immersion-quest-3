package dev.dioxus.main

import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.view.ViewGroup
import android.webkit.WebView
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat

// dx copies this file verbatim (no template rendering), so the package id is spelled out.
typealias BuildConfig = dev.molipquest.app.BuildConfig

/// Draws the page edge to edge so the status bar takes the colour of whatever the app
/// renders at the top (green classroom, dark practice header) instead of a grey strip.
/// The real inset sizes are handed to CSS as --inset-top / --inset-bottom.
class MainActivity : WryActivity() {
    private var insetTop = 0f
    private var insetBottom = 0f

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        WindowCompat.setDecorFitsSystemWindows(window, false)
        window.statusBarColor = Color.TRANSPARENT
        window.navigationBarColor = Color.TRANSPARENT
        val controller = WindowCompat.getInsetsController(window, window.decorView)
        controller.isAppearanceLightStatusBars = false
        controller.isAppearanceLightNavigationBars = false

        val content = findViewById<View>(android.R.id.content)
        ViewCompat.setOnApplyWindowInsetsListener(content) { view, insets ->
            val bars = insets.getInsets(
                WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.displayCutout()
            )
            val ime = insets.getInsets(WindowInsetsCompat.Type.ime())
            val keyboardOpen = ime.bottom > bars.bottom
            // Shrink the page while the keyboard is up so quiz inputs stay visible.
            view.setPadding(0, 0, 0, if (keyboardOpen) ime.bottom else 0)
            val density = resources.displayMetrics.density
            insetTop = bars.top / density
            insetBottom = if (keyboardOpen) 0f else bars.bottom / density
            applyInsets()
            WindowInsetsCompat.CONSUMED
        }
        // The WebView and its document appear after onCreate; re-apply until the page has them.
        for (delay in longArrayOf(300, 1000, 2500, 5000)) {
            content.postDelayed({ applyInsets() }, delay)
        }
        ViewCompat.requestApplyInsets(content)
    }

    override fun onResume() {
        super.onResume()
        applyInsets()
    }

    private fun applyInsets() {
        val webView = findWebView(window.decorView) ?: return
        webView.evaluateJavascript(
            "document.documentElement.style.setProperty('--inset-top','${insetTop}px');" +
                "document.documentElement.style.setProperty('--inset-bottom','${insetBottom}px');",
            null
        )
    }

    private fun findWebView(view: View): WebView? {
        if (view is WebView) return view
        if (view is ViewGroup) {
            for (index in 0 until view.childCount) {
                findWebView(view.getChildAt(index))?.let { return it }
            }
        }
        return null
    }
}
