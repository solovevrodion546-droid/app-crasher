package org.appcrasher.crasher;

import android.app.ListActivity;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
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

        PackageManager pm = getPackageManager();

        List<PackageInfo> packages = pm.getInstalledPackages(0);
        for (PackageInfo pkg : packages) {
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
            crashApp(selected.packageName, selected.name);
        });
    }

    private void crashApp(String packageName, String appName) {
        try {
            Process process = Runtime.getRuntime().exec(
                new String[]{"am", "force-stop", packageName});
            process.waitFor();
            Toast.makeText(this, "✅ " + appName + " выплотела!", Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Toast.makeText(this, "⚠️ Не удалось: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
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
