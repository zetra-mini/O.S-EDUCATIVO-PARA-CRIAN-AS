package br.com.jarviskids.os;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.text.InputType;
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
    private static final String FALLBACK_LOCAL_URL = "file:///android_asset/painel_pais.html";

    private WebView webView;
    private PermissionRequest pendingPermissionRequest;
    private SharedPreferences prefs;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Tela cheia imersiva permanente e mantem tela ligada
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        hideSystemUI();

        prefs = getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);

        webView = new WebView(this);
        setContentView(webView);

        configurarWebView();
        solicitarPermissoesNativas();

        // Recupera URL configurada pelo pai/mãe
        String targetUrl = prefs.getString(KEY_SERVER_URL, "");

        // Se nunca configurou ou se ainda tinha o dominio de exemplo (novaflix.app.br), exibe o seletor
        if (targetUrl == null || targetUrl.trim().isEmpty() || targetUrl.contains("novaflix.app.br")) {
            exibirDialogoPrimeiroAcesso();
        } else {
            conectar(targetUrl);
        }
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

        // Habilita assets locais offline
        settings.setAllowFileAccess(true);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setSupportMultipleWindows(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(false);

        webView.setWebViewClient(new WebViewClient() {
            private String normalizarUrl(String url) {
                if (url == null || url.trim().isEmpty()) return FALLBACK_LOCAL_URL;
                if (url.endsWith("/pais") || url.equals("file:///pais") || url.contains("/pais")) {
                    return FALLBACK_LOCAL_URL;
                }
                return url;
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                view.loadUrl(normalizarUrl(url));
                return true;
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    view.loadUrl(normalizarUrl(request.getUrl().toString()));
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
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                runOnUiThread(() -> {
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
                });
            }
        });

        // Toque longo em qualquer área abre menu rápido de conexão
        webView.setOnLongClickListener(v -> {
            exibirMenuModo();
            return true;
        });
    }

    private void lidarComErroConexao(String url) {
        if (url != null && url.startsWith("file:")) {
            return;
        }

        runOnUiThread(() -> {
            AlertDialog.Builder builder = new AlertDialog.Builder(MainActivity.this);
            builder.setTitle("📡 Falha na Conexão");
            builder.setMessage("Não foi possível conectar ao Jarvis OS em:\n" + url + "\n\nO netbook está ligado e conectado na mesma rede ou com o túnel ativo?");
            builder.setCancelable(false);

            builder.setPositiveButton("🔄 Tentar Novamente", (d, w) -> {
                conectar(url);
            });

            builder.setNeutralButton("⚙️ Trocar Conexão", (d, w) -> {
                exibirMenuModo();
            });

            builder.setNegativeButton("📱 Usar Modo Offline", (d, w) -> {
                webView.loadUrl(FALLBACK_LOCAL_URL);
                Toast.makeText(MainActivity.this, "Painel dos Pais Offline carregado!", Toast.LENGTH_SHORT).show();
            });

            builder.show();
        });
    }

    private void conectar(String url) {
        if (url == null || url.trim().isEmpty()) {
            url = FALLBACK_LOCAL_URL;
        } else {
            url = url.trim();
            if (!url.startsWith("http://") && !url.startsWith("https://") && !url.startsWith("file://")) {
                url = "http://" + url;
            }
            if (!url.endsWith("/admin") && !url.startsWith("file:")) {
                if (url.endsWith("/")) {
                    url += "admin";
                } else {
                    url += "/admin";
                }
            }
        }
        prefs.edit().putString(KEY_SERVER_URL, url).apply();
        webView.loadUrl(url);
    }

    private void exibirDialogoPrimeiroAcesso() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("🚀 Conexão Jarvis Kids Mobile");
        builder.setMessage("Como você deseja conectar o aplicativo ao Jarvis OS?");
        builder.setCancelable(false);

        String[] opcoes = {
            "🏠 1. Rede Wi-Fi de Casa (IP Local, ex: 192.168.1.X:8000)",
            "⚡ 2. Túnel Remoto Cloudflare (URL trycloudflare.com ou domínio)",
            "📱 3. Modo Local Offline (Sem Robô Conectado)"
        };

        builder.setItems(opcoes, (dialog, which) -> {
            if (which == 0) {
                solicitarIpLocal();
            } else if (which == 1) {
                solicitarUrlNuvem();
            } else {
                conectar(FALLBACK_LOCAL_URL);
            }
        });
        builder.show();
    }

    private void exibirMenuModo() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("⚙️ Configurações de Conexão");
        String[] opcoes = {
            "🏠 Conectar via Wi-Fi de Casa (IP Local)",
            "⚡ Conectar via Túnel Cloudflare (Remoto)",
            "📱 Abrir Painel Offline",
            "🔄 Recarregar Página Atual"
        };

        builder.setItems(opcoes, (dialog, which) -> {
            if (which == 0) {
                solicitarIpLocal();
            } else if (which == 1) {
                solicitarUrlNuvem();
            } else if (which == 2) {
                conectar(FALLBACK_LOCAL_URL);
            } else if (which == 3) {
                webView.reload();
            }
        });
        builder.setNegativeButton("Fechar", null);
        builder.show();
    }

    private void solicitarIpLocal() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("🏠 Conexão Wi-Fi Local (Casa)");
        builder.setMessage("Digite o IP do netbook exibido na aba 'Conexão Remota' do painel (ex: 192.168.1.105:8000):");

        final EditText input = new EditText(this);
        input.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_URI);
        input.setHint("192.168.1.105:8000");
        String saved = prefs.getString(KEY_SERVER_URL, "");
        if (saved != null && saved.contains("192.168.")) {
            input.setText(saved.replace("http://", "").replace("/admin", ""));
        }
        builder.setView(input);

        builder.setPositiveButton("Conectar", (dialog, which) -> {
            String valor = input.getText().toString().trim();
            if (!valor.isEmpty()) {
                conectar("http://" + valor);
            }
        });
        builder.setNegativeButton("Cancelar", null);
        builder.show();
    }

    private void solicitarUrlNuvem() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("⚡ Conexão Remota Cloudflare");
        builder.setMessage("Cole o link gerado no botão 'Túnel Rápido' (ex: https://xxx.trycloudflare.com) ou seu domínio próprio:");

        final EditText input = new EditText(this);
        input.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_URI);
        input.setHint("https://seu-tunel.trycloudflare.com");
        String saved = prefs.getString(KEY_SERVER_URL, "");
        if (saved != null && (saved.contains("trycloudflare.com") || saved.contains("https://"))) {
            input.setText(saved);
        }
        builder.setView(input);

        builder.setPositiveButton("Conectar", (dialog, which) -> {
            String valor = input.getText().toString().trim();
            if (!valor.isEmpty()) {
                conectar(valor);
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
