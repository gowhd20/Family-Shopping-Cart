package com.example.arash.shoppinglist;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.database.Cursor;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

public class DetailsItemActivity extends AppCompatActivity {

    DatabaseHelper database;
    TextView Name_textView, WhoAsked_textView, NeedTime_textView, Place_textView, Price_textView, Receivers_textView, Description_textView;
    String itemName, itemID;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_details_item);

        database = new DatabaseHelper(this);
        Name_textView = (TextView)findViewById(R.id.DetailsName_textView);
        WhoAsked_textView = (TextView)findViewById(R.id.DetailsWhoAsked_textView);
        NeedTime_textView = (TextView)findViewById(R.id.DetailsNeedTime_textView);
        Place_textView = (TextView)findViewById(R.id.DetailsPlace_textView);
        Price_textView = (TextView)findViewById(R.id.DetailsPrice_textView);
        Receivers_textView = (TextView)findViewById(R.id.DetailsReceivers_textView);
        Description_textView =(TextView)findViewById(R.id.DetailsDescription_textView);

        ShowItemDetails();
    }

    public void ShowItemDetails() {
        Cursor res = database.getAllItemData();
        int index = 0;
        if (res.getCount()> 0){
            while (res.moveToNext()) {
                if (index == ShoppingListActivity.SelectedShoppingItemPosition) {
                    itemName = res.getString(1);
                    Name_textView.setText(res.getString(1));
                    WhoAsked_textView.setText("- Requested by '" + res.getString(9) + "'");
                    if (Integer.valueOf(res.getString(3)) < 10)
                        NeedTime_textView.setText("- Is needed before " + res.getString(2) + ":0" + res.getString(3));
                    else
                        NeedTime_textView.setText("- Is needed before " + res.getString(2) + ":" + res.getString(3));
                    Place_textView.setText("- Can be found at " + res.getString(6));
                    Price_textView.setText("- Price is around " + res.getString(5));
                    Receivers_textView.setText(res.getString(7));
                    Description_textView.setText(res.getString(10));
                    itemID = res.getString(11);
                }
                index++;
            }
        }
    }

    public void ShoppingListItem_remove(View view){
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder
                .setTitle("Deleting the item !")
                .setMessage(" Are you sure?")
                .setIcon(android.R.drawable.ic_dialog_alert)
                .setPositiveButton("Yes", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        //delete the Item
                        DeleteShoppingItem deleteShoppingItem = new DeleteShoppingItem(DetailsItemActivity.this, itemID);
                        deleteShoppingItem.execute();
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

    public void IWillBuy (View view){
        JsonObject obj = new JsonObject();
        JsonObject inner_obj = new JsonObject();
        JsonObject data_obj = new JsonObject();
        JsonArray inner_array = new JsonArray();

        obj.addProperty("uuid", FamilyGroupActivity.familyID_static);
        obj.addProperty("req_uuid", itemID);
        inner_obj.addProperty("uid", FamilyGroupActivity.userID_static);
        inner_array.add(inner_obj);
        data_obj.add("acceptors", inner_array);
        obj.add("data_to_update", data_obj);

        AddAcceptors addAcceptors = new AddAcceptors(this, obj);
        addAcceptors.execute();
    }

    @Override
    protected void onResume() {
        super.onResume();
        MainActivity.activityTracker = "DetailsItemActivity";
    }
}
