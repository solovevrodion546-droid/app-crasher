package org.appcrasher.crasher;

import android.app.Service;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.widget.Toast;
import java.util.HashSet;
import java.util.Set;
import java.util.Timer;
import java.util.TimerTask;

public class CrashService extends Service {

    private Timer monitorTimer;
    private Handler handler;
    private Set<String> targetPackages = new HashSet<>();
    private PackageManager pm;
    private static final long CHECK_INTERVAL = 3000; // 3 секунды

    @Override
    public void onCreate() {
        super.onCreate();
        pm = getPackageManager();
        handler = new Handler(Looper.getMainLooper());
        
        // Foreground service — Huawei не убьёт с уведомлением
        android.app.Notification notification = new android.app.Notification.Builder(this, "crash_channel")
            .setContentTitle("AppCrasher v2")
            .setContentText("Мониторинг запущен! Нажми на приложение чтобы выплотить.")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .build();
        
        startForeground(1, notification);
        
        // Запускаем мониторинг
        startMonitoring();
    }

    private void startMonitoring() {
        monitorTimer = new Timer();
        monitorTimer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                for (String pkg : targetPackages) {
                    try {
                        // Пытаемся получить название приложения
                        CharSequence name = "Приложение";
                        try {
                            name = pm.getApplicationLabel(pm.getApplicationInfo(pkg, 0));
                        } catch (Exception ignored) {}
                        
                        // force-stop — работает на Huawei
                        Runtime.getRuntime().exec(new String[]{"am", "force-stop", pkg});
                        
                        // Показываем результат
                        final CharSequence finalName = name;
                        handler.post(() -> {
                            Toast.makeText(CrashService.this, "✅ " + finalName + " выплотела!", 
                                Toast.LENGTH_LONG).show();
                        });
                    } catch (Exception e) {
                        // Игнорируем ошибки
                    }
                }
            }
        }, 0, CHECK_INTERVAL);
    }

    public void addTargetPackage(String packageName) {
        targetPackages.add(packageName);
    }

    public void clearTargets() {
        targetPackages.clear();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (monitorTimer != null) {
            monitorTimer.cancel();
        }
    }
}
