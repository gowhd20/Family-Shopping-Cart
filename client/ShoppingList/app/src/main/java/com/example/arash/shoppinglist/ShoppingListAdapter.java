package com.example.arash.shoppinglist;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import java.util.ArrayList;

/**
 * Created by Arash on 4/15/2016.
 */
public class ShoppingListAdapter extends ArrayAdapter {
    public ShoppingListAdapter(Context context, ArrayList<String> itemsName) {
        super(context, R.layout.shopping_list_items,itemsName);
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        LayoutInflater layoutInflater = LayoutInflater.from(getContext());
        View customView = layoutInflater.inflate(R.layout.shopping_list_items, parent, false);

        TextView itemName_textView = (TextView) customView.findViewById(R.id.ShoppingListItemName_textView);
        TextView itemWhoBuy_textView = (TextView) customView.findViewById(R.id.ShoppingListItemWhoBuy_textView);
        ImageView itemUrgency_imageView = (ImageView) customView.findViewById(R.id.shoppingItemUrgent_icon);

        itemName_textView.setText(ShoppingListActivity.ItemsList_Name.get(position));
        itemWhoBuy_textView.setText(ShoppingListActivity.ItemsList_WhoBuy.get(position));
        if(ShoppingListActivity.ItemsList_Urgency.get(position)==1)
            itemUrgency_imageView.setImageResource(R.drawable.urgent);
        else
            itemUrgency_imageView.setImageResource(R.drawable.urgent_empty);

        //set background
        if (ShoppingListActivity.SelectedShoppingItemPosition != null){
            if (ShoppingListActivity.SelectedShoppingItemPosition == position)
                customView.setBackgroundResource(R.drawable.shopping_list_background_selected);
            else
                customView.setBackgroundResource(R.drawable.shopping_list_background_normal);
        }

        return customView;
    }
}
