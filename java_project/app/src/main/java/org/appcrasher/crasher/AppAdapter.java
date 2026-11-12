package org.appcrasher.crasher;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;
import java.util.List;

public class AppAdapter extends ArrayAdapter<MainActivity.AppItem> {
    private final Context context;
    private final List<MainActivity.AppItem> items;

    public AppAdapter(Context context, List<MainActivity.AppItem> items) {
        super(context, 0, items);
        this.context = context;
        this.items = items;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        if (convertView == null) {
            convertView = LayoutInflater.from(context)
                .inflate(android.R.layout.simple_list_item_2, parent, false);
        }

        MainActivity.AppItem item = items.get(position);
        ((TextView) convertView.findViewById(android.R.id.text1)).setText(item.name);
        ((TextView) convertView.findViewById(android.R.id.text2)).setText(item.packageName);
        
        ImageView icon = convertView.findViewById(android.R.id.icon);
        if (icon != null && item.icon != null) {
            icon.setImageDrawable(item.icon);
        }

        return convertView;
    }
}
