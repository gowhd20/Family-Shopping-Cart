package com.example.arash.shoppinglist;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.database.Cursor;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonArray;

import java.util.ArrayList;
import java.util.List;

public class ShoppingListActivity extends AppCompatActivity {

    DatabaseHelper database;
    public static ArrayList<String> ItemsList_Name = new ArrayList<String>();
    public static ArrayList<String> ItemsList_WhoBuy = new ArrayList<String>();
    public static ArrayList<Integer> ItemsList_Urgency = new ArrayList<Integer>();
    public static Integer SelectedShoppingItemPosition;
    public static String SelectedShoppingItemName;
    int newItems_count = 0, newItem_index = 0;
    String CurrentDisplayedNewItemName = "";
    ListView shoppingListView;
    ArrayAdapter<String> adapter; // A STRING ADAPTER WHICH WILL HANDLE THE DATA OF THE LISTVIEW
    String activeItemValue;
    ImageView addItem_imageView, CreateNewItem_imageView, nextNewItem_imageView, previousNewItem_imageView, trashcan_imageView;
    TextView newItem_textView, newItemsCount_textView;
    public static Boolean NotificationComes = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_shopping_list);

        database = new DatabaseHelper(this);
        addItem_imageView = (ImageView)findViewById(R.id.ShoppingListAddItem_ImageView);
        CreateNewItem_imageView = (ImageView)findViewById(R.id.CreateNewItem_imageView);
        nextNewItem_imageView = (ImageView)findViewById(R.id.next_imageView);
        previousNewItem_imageView = (ImageView)findViewById(R.id.previous_imageView);
        trashcan_imageView =(ImageView)findViewById(R.id.trashcan_imageView);
        newItem_textView = (TextView)findViewById(R.id.newItemDetails_textView);
        newItemsCount_textView = (TextView)findViewById(R.id.newItemsCount_textView);
        shoppingListView =(ListView)findViewById(R.id.Shopping_listView);
        updateShoppingList_arrays();
        adapter = new ShoppingListAdapter(this, ItemsList_Name);
        shoppingListView.setAdapter(adapter);

        // ListView Item Click Listener
        shoppingListView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                SelectedShoppingItemPosition = position;
                SelectedShoppingItemName = (String) shoppingListView.getItemAtPosition(position);
                activeItemValue = (String) shoppingListView.getItemAtPosition(position);
                // recreate shopping list to change selected item background
                updateShoppingList();

                //Show selected item details
                Intent intent = new Intent(ShoppingListActivity.this, DetailsItemActivity.class);
                startActivity(intent);
            }
        });

        //update shopping list
        updateShoppingList();
    }

    public void CreateNewItem(View view){
        Cursor res = database.getAllMembersData();
        if (res.getCount()>0){
            Intent intent = new Intent(this, AddItem.class);
            startActivity(intent);
        }
        else
            Toast.makeText(ShoppingListActivity.this, "Family member group is empty !", Toast.LENGTH_SHORT).show();
    }

    public void AddToShoppingCart(View view){
        if (newItems_count>0){
            Cursor res = database.getAllNewItemData();
            newItems_count = res.getCount();

            JsonObject obj = new JsonObject();
            JsonObject inner_obj= new JsonObject();
            JsonArray jsonItemsArray = new JsonArray();
            JsonObject item_obj;
            JsonArray jsonArray;

            obj.addProperty("uuid", FamilyGroupActivity.familyID_static);
            inner_obj.addProperty("uid", FamilyGroupActivity.userID_static);
            obj.add("sender", inner_obj);

            while (res.moveToNext()){
                String itemName = res.getString(1);
                int itemTimeHour = res.getInt(2);
                int itemTimeMin = res.getInt(3);
                int itemUrgency = res.getInt(4);
                String itemPrice = res.getString(5);
                String itemPlace = res.getString(6);
                String itemWhoBuy = "";
                String itemDescription = res.getString(8);
                String receiversID_str = res.getString(9);
                String[] receiversID_array =receiversID_str.split(", ");

                item_obj = new JsonObject();
                jsonArray = new JsonArray();
                item_obj.addProperty("item", itemName);
                int i=0;
                // create receivers
                for (i=0; i<receiversID_array.length; i++){
                    inner_obj = new JsonObject();
                    inner_obj.addProperty("uid", receiversID_array[i]);
                    jsonArray.add(inner_obj);}
                item_obj.add("receivers", jsonArray);
                //optional
                jsonArray = new JsonArray();
                inner_obj = new JsonObject();
                inner_obj.addProperty("price", itemPrice);
                inner_obj.addProperty("description", itemDescription);
                inner_obj.addProperty("location", itemPlace);
                inner_obj.addProperty("urgency", itemUrgency);
                // This approach is better to be replaced with Unix (epoch) time, But for that date of need also is needed.
                int timeNeed = (itemTimeHour * 100) + itemTimeMin;
                inner_obj.addProperty("time_of_need", timeNeed);
//            jsonArray.add(inner_obj);
//            item_obj.add("optional_data", jsonArray);
                item_obj.add("optional_data", inner_obj);


                jsonItemsArray.add(item_obj);
            }
            obj.add("requests", jsonItemsArray);
            Log.d("main", "obj:  " + obj);
            CreateShoppingItem createShoppingItem = new CreateShoppingItem(this, obj);
            createShoppingItem.execute();

            database.clearNewItems();
        }
    }

    public void updateShoppingCartLocalDatabase(){
        GetShoppingCart getShoppingCart = new GetShoppingCart(this, FamilyGroupActivity.familyID_static);
        getShoppingCart.execute();
    }

    public void updateShoppingList(){
        Cursor res = database.getAllItemData();
        if (res.getCount()==0){
            ItemsList_Name.clear();
            ItemsList_WhoBuy.clear();
            ItemsList_Urgency.clear();
            adapter.notifyDataSetChanged(); // Check if the adapter has changed
        }
        else{
            ItemsList_Name.clear();
            ItemsList_WhoBuy.clear();
            ItemsList_Urgency.clear();
            while (res.moveToNext()) {
                //update list of family members
                ItemsList_Name.add(res.getString(1)); // Add items "name" to your array for listView
                ItemsList_WhoBuy.add(res.getString(8)); // Add items "WhoBuy"  to your array for listView
                ItemsList_Urgency.add(res.getInt(4)); // Add items "Urgency"  to your array for listView
                adapter.notifyDataSetChanged(); // Check if the adapter has changed
            }
        }
    }

    public void updateShoppingList_arrays(){
        Cursor res = database.getAllItemData();
        if (res.getCount()==0){
            ItemsList_Name.clear();
            ItemsList_WhoBuy.clear();
            ItemsList_Urgency.clear();
        }
        else{
            ItemsList_Name.clear();
            ItemsList_WhoBuy.clear();
            ItemsList_Urgency.clear();
            while (res.moveToNext()) {
                //update list of family members
                ItemsList_Name.add(res.getString(1)); // Add items "name" to your array for listView
                ItemsList_WhoBuy.add(res.getString(8)); // Add items "WhoBuy"  to your array for listView
                ItemsList_Urgency.add(res.getInt(4)); // Add items "Urgency"  to your array for listView
            }
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        MainActivity.activityTracker = "ShoppingListActivity";

        // if notification comes updateShoppingCartDatabase
        if(NotificationComes == true){
            GetShoppingCart getShoppingCart = new GetShoppingCart(this, FamilyGroupActivity.familyID_static);
            getShoppingCart.execute();
            NotificationComes = false;
        }

        SelectedShoppingItemPosition = null;
        SelectedShoppingItemName = null;
        //update shopping list
        updateShoppingList();

        // check for temporary new items
        Cursor res = database.getAllNewItemData();
        newItems_count = res.getCount();
        updateNewItemsPanel();

    }

    public void next_newItem(View view){
        if (newItems_count>1){
            previousNewItem_imageView.setImageResource(R.drawable.left_arrow_3_blue);
            if (newItem_index<(newItems_count-1)){
                ++newItem_index;
                showNewItem(newItem_index);
                if (newItem_index==(newItems_count-1)) {
                    nextNewItem_imageView.setImageResource(R.drawable.right_arrow_3_grey);
                }
            }
        }
    }

    public void previous_newItem(View view){
        if (newItems_count>1){
            nextNewItem_imageView.setImageResource(R.drawable.right_arrow_3_blue);
            if (newItem_index>0){
                --newItem_index;
                showNewItem(newItem_index);
                if (newItem_index==0) {
                    previousNewItem_imageView.setImageResource(R.drawable.left_arrow_3_grey);
                }
            }
        }
    }

    public void showNewItem(int index){
        Cursor res = database.getAllNewItemData();
        int pointer = 0;
        if (res.getCount()>0){
            while (res.moveToNext()) {
                if (pointer == index) {
                    CurrentDisplayedNewItemName = res.getString(1);
                    String str1 = "- Item name:  " + res.getString(1) + "\n";
                    String hour, min;
                    if (Integer.valueOf(res.getString(3))<10)
                        min = "0" + res.getString(3);
                    else
                        min = res.getString(3);
                    if (Integer.valueOf(res.getString(2))<10)
                        hour = "0" + res.getString(2);
                    else
                        hour = res.getString(2);
                    String str2 = "- Time of need:  " + hour + ":" + min + "\n";
                    String str3;
                    if (res.getInt(4) == 1)
                        str3 = "- Urgent\n";
                    else
                        str3 = "";
                    String str4 = "- Estimated price:  " + res.getString(5) + "\n";
                    String str5 = "- Available at:  " + res.getString(6) + "\n";
                    String str6 = "- Receivers:  " + res.getString(7) + "\n";
                    String str7 = "- Description  :  " + res.getString(8) + "\n";

                    String itemDetails_str = str1 + str2 + str3 + str4 + str5 + str6 + str7;
                    newItem_textView.setText(itemDetails_str);
                }
                ++pointer;
            }
        }
    }

    public void updateNewItemsPanel(){
        Cursor res = database.getAllNewItemData();
        newItems_count = res.getCount();
        if (newItems_count>0) {
            //show related views
            if (newItems_count == 1) {
                nextNewItem_imageView.setImageResource(R.drawable.right_arrow_3_grey);
                previousNewItem_imageView.setImageResource(R.drawable.left_arrow_3_grey);}
            else{
                nextNewItem_imageView.setImageResource(R.drawable.right_arrow_3_blue);
                previousNewItem_imageView.setImageResource(R.drawable.left_arrow_3_blue);
                if(newItem_index==0)
                    previousNewItem_imageView.setImageResource(R.drawable.left_arrow_3_grey);
                if(newItem_index==(newItems_count-1))
                    nextNewItem_imageView.setImageResource(R.drawable.right_arrow_3_grey);
            }
            newItem_textView.setBackgroundResource(R.drawable.new_item_details);
            showNewItem(newItem_index);
            trashcan_imageView.setImageResource(R.drawable.trashcan);
            addItem_imageView.setImageResource(R.drawable.add_cart_blue);
            newItemsCount_textView.setText(String.valueOf(newItems_count));
            newItemsCount_textView.setBackgroundResource(R.drawable.red_circle_background);
        }
        else{
            //hide related views
            nextNewItem_imageView.setImageResource(R.drawable.plus_empty);
            previousNewItem_imageView.setImageResource(R.drawable.plus_empty);
            newItem_textView.setBackgroundResource(R.drawable.transparent_background);
            newItem_textView.setText("");
            trashcan_imageView.setImageResource(R.drawable.plus_empty);
            addItem_imageView.setImageResource(R.drawable.add_cart_grey);
            newItemsCount_textView.setText("");
            newItemsCount_textView.setBackgroundResource(R.drawable.transparent_background);
        }
    }

    public void removeNewItem(View view){
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder
                .setTitle("Deleting the item !")
                .setMessage(" Are you sure?")
                .setIcon(android.R.drawable.ic_dialog_alert)
                .setPositiveButton("Yes", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        //delete the Item
                        Integer removeRows = database.removeNewItem(CurrentDisplayedNewItemName);
                        --newItem_index;
                        updateNewItemsPanel();
                    }
                });
        builder.setNegativeButton("No", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int which) {
                dialog.dismiss();
            }
        });
        AlertDialog alert = builder.create();
        alert.show();
    }

}
