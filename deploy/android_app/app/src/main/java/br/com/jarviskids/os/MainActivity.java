package br.com.jarviskids.os;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.EditText;
import android.widget.Toast;

public class MainActivity extends Activity {

    private static final int PERMISSION_REQUEST_CODE = 1001;
    private static final String PREF_NAME = "JarvisKidsPrefs";
    private static final String KEY_SERVER_URL = "server_url";
    private static final String DEFAULT_LOCAL_URL = "file:///android_asset/hud_jarvis.html";

    private WebView webView;
    private PermissionRequest pendingPermissionRequest;
    private SharedPreferences prefs;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Tela cheia e manter tela ligada
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        hideSystemUI();

        prefs = getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);

        webView = new WebView(this);
        setContentView(webView);

        configurarWebView();
        solicitarPermissoesNativas();

        // Inicializacao 100% autonoma por padrao: carrega os assets locais embutidos
        String targetUrl = prefs.getString(KEY_SERVER_URL, DEFAULT_LOCAL_URL);
        if (targetUrl == null || targetUrl.trim().isEmpty() || targetUrl.contains("127.0.0.1:8000")) {
            targetUrl = DEFAULT_LOCAL_URL;
        }

        webView.loadUrl(targetUrl);
    }

    private void hideSystemUI() {
        View decorView = getWindow().getDecorView();
        decorView.setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
        );
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            hideSystemUI();
        }
    }

    private void configurarWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        
        // Habilita acesso total a arquivos e assets locais offline
        settings.setAllowFileAccess(true);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setSupportMultipleWindows(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(false);

        webView.setWebViewClient(new WebViewClient() {
            private String normalizarUrl(String url) {
                if (url == null || url.trim().isEmpty()) return DEFAULT_LOCAL_URL;
                if (url.endsWith("/pais") || url.equals("file:///pais") || url.contains("/pais")) {
                    return "file:///android_asset/painel_pais.html";
                }
                if (url.equals("file:///") || url.endsWith("/hud_jarvis.html")) {
                    return "file:///android_asset/hud_jarvis.html";
                }
                return url;
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                String target = normalizarUrl(url);
                view.loadUrl(target);
                return true;
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    String url = request.getUrl().toString();
                    String target = normalizarUrl(url);
                    view.loadUrl(target);
                    return true;
                }
                return false;
            }

            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                lidarComErroConexao(failingUrl);
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    if (request.isForMainFrame()) {
                        lidarComErroConexao(request.getUrl().toString());
                    }
                }
            }

            private void lidarComErroConexao(String url) {
                if (url != null && url.startsWith("file:")) {
                    return; // Arquivos locais em assets nao geram aviso de Wi-Fi
                }
                // Em caso de falha de conexao com IP externo, reverte imediatamente para o modo autonomo offline!
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        Toast.makeText(MainActivity.this, "Robô na rede Wi-Fi não encontrado. Modo Autônomo Offline Ativado!", Toast.LENGTH_LONG).show();
                        prefs.edit().putString(KEY_SERVER_URL, DEFAULT_LOCAL_URL).apply();
                        webView.loadUrl(DEFAULT_LOCAL_URL);
                    }
                });
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                            for (String res : request.getResources()) {
                                if (PermissionRequest.RESOURCE_AUDIO_CAPTURE.equals(res)) {
                                    pendingPermissionRequest = request;
                                    if (checkSelfPermission(android.Manifest.permission.RECORD_AUDIO)
                                            == PackageManager.PERMISSION_GRANTED) {
                                        request.grant(request.getResources());
                                    } else {
                                        requestPermissions(
                                                new String[]{android.Manifest.permission.RECORD_AUDIO},
                                                PERMISSION_REQUEST_CODE);
                                    }
                                    return;
                                }
                            }
                        }
                        request.grant(request.getResources());
                    }
                });
            }
        });

        // Toque longo com 2 dedos para abrir menu de conexao
        webView.setOnLongClickListener(new View.OnLongClickListener() {
            @Override
            public boolean onLongClick(View v) {
                exibirMenuModo();
                return true;
            }
        });
    }

    private void exibirMenuModo() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("⚙️ Modo do JARVIS Kids Mobile");
        String[] opcoes = {
            "🎮 Modo Autônomo Offline (Jogar Direto no Celular)",
            "👨‍👩‍👧 Painel dos Pais (Autônomo Local)",
            "📡 Conectar ao Netbook / PC na Rede Wi-Fi"
        };

        builder.setItems(opcoes, (dialog, which) -> {
            if (which == 0) {
                prefs.edit().putString(KEY_SERVER_URL, DEFAULT_LOCAL_URL).apply();
                webView.loadUrl(DEFAULT_LOCAL_URL);
                Toast.makeText(MainActivity.this, "Modo Autônomo Ativado!", Toast.LENGTH_SHORT).show();
            } else if (which == 1) {
                String paisUrl = "file:///android_asset/painel_pais.html";
                webView.loadUrl(paisUrl);
            } else if (which == 2) {
                solicitarIpServidor();
            }
        });
        builder.show();
    }

    private void solicitarIpServidor() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Conectar ao Robô na Rede");
        builder.setMessage("Digite o IP do Netbook ou Computador (Ex: 192.168.1.100:8000):");

        final EditText input = new EditText(this);
        input.setHint("Ex: 192.168.1.100:8000");
        builder.setView(input);

        builder.setPositiveButton("Conectar", (dialog, which) -> {
            String ip = input.getText().toString().trim();
            if (!ip.isEmpty()) {
                if (!ip.startsWith("http://") && !ip.startsWith("https://")) {
                    ip = "http://" + ip;
                }
                prefs.edit().putString(KEY_SERVER_URL, ip).apply();
                webView.loadUrl(ip);
            }
        });
        builder.setNegativeButton("Cancelar", null);
        builder.show();
    }

    private void solicitarPermissoesNativas() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (checkSelfPermission(android.Manifest.permission.RECORD_AUDIO)
                    != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(
                        new String[]{android.Manifest.permission.RECORD_AUDIO},
                        PERMISSION_REQUEST_CODE);
            }
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQUEST_CODE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                if (pendingPermissionRequest != null) {
                    pendingPermissionRequest.grant(pendingPermissionRequest.getResources());
                    pendingPermissionRequest = null;
                }
            }
        }
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
