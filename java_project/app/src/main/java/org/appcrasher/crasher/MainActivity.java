package org.appcrasher.crasher;

import android.app.ListActivity;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.widget.Toast;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

public class MainActivity extends ListActivity {

    private List<AppItem> appList = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Создаём Notification Channel (нужен для Foreground Service)
        createNotificationChannel();
        
        // Запускаем сервис
        startService(new Intent(this, CrashService.class));
        
        // Загружаем список приложений
        populateAppList();
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                "crash_channel",
                "AppCrasher",
                NotificationManager.IMPORTANCE_LOW
            );
            channel.setDescription("Мониторинг выпоты приложений");
            NotificationManager manager = getSystemService(NotificationManager.class);
            if (manager != null) {
                manager.createNotificationChannel(channel);
            }
        }
    }

    private void populateAppList() {
        android.content.pm.PackageManager pm = getPackageManager();
        List<android.content.pm.PackageInfo> packages = pm.getInstalledPackages(0);
        
        for (android.content.pm.PackageInfo pkg : packages) {
            if ((pkg.applicationInfo.flags & android.content.pm.ApplicationInfo.FLAG_SYSTEM) == 0) {
                CharSequence name = pkg.applicationInfo.loadLabel(pm);
                if (name != null && !name.toString().isEmpty()) {
                    appList.add(new AppItem(name.toString(), pkg.packageName,
                            pkg.applicationInfo.loadIcon(pm)));
                }
            }
        }
        
        Collections.sort(appList, (a, b) -> a.name.compareTo(b.name));
        setListAdapter(new AppAdapter(this, appList));
        
        getListView().setOnItemClickListener((parent, view, position, id) -> {
            AppItem selected = appList.get(position);
            Toast.makeText(this, "🎯 " + selected.name + " выплотит при запуске!", 
                Toast.LENGTH_LONG).show();
        });
    }

    static class AppItem {
        String name;
        String packageName;
        android.graphics.drawable.Drawable icon;

        AppItem(String name, String packageName, android.graphics.drawable.Drawable icon) {
            this.name = name;
            this.packageName = packageName;
            this.icon = icon;
        }
    }
}
