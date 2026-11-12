package org.appcrasher.crasher;

import android.app.Service;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.widget.Toast;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.Timer;
import java.util.TimerTask;

public class CrashService extends Service {

    private Timer monitorTimer;
    private Handler handler;
    private Set<String> targetPackages = new HashSet<>();
    private PackageManager pm;
    private static final long CHECK_INTERVAL = 2000; // 2 секунды

    @Override
    public void onCreate() {
        super.onCreate();
        pm = getPackageManager();
        handler = new Handler(Looper.getMainLooper());
        
        // Создаём уведомление для foreground service (чтобы Huawei не убивал)
        android.app.Notification notification = new android.app.Notification.Builder(this, "crash_channel")
            .setContentTitle("AppCrasher")
            .setContentText("Мониторинг запущен...")
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
                checkAndCrash();
            }
        }, 0, CHECK_INTERVAL);
    }

    private void checkAndCrash() {
        for (String pkg : targetPackages) {
            try {
                // Проверяем запущен ли пакет
                if (isAppRunning(pkg)) {
                    // Убиваем
                    Runtime.getRuntime().exec(new String[]{"am", "force-stop", pkg});
                    // Показываем уведомление
                    showCrashed(pkg);
                }
            } catch (Exception e) {
                // Игнорируем
            }
        }
    }

    private boolean isAppRunning(String packageName) {
        try {
            List<android.app.ActivityManager.RunningAppProcessInfo> processes =
                ((android.app.ActivityManager) getSystemService(ACTIVITY_SERVICE))
                    .getRunningAppProcesses();
            for (android.app.ActivityManager.RunningAppProcessInfo proc : processes) {
                if (proc.processName != null && proc.processName.startsWith(packageName)) {
                    return true;
                }
            }
            return false;
        } catch (Exception e) {
            return false;
        }
    }

    private void showCrashed(String pkg) {
        CharSequence name = "";
        try {
            name = pm.getApplicationLabel(pm.getApplicationInfo(pkg, 0));
        } catch (PackageManager.NameNotFoundException e) {
            name = pkg;
        }
        
        handler.post(() -> {
            Toast.makeText(CrashService.this, "✅ " + name + " выплотела!", 
                Toast.LENGTH_SHORT).show();
        });
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
