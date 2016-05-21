package com.example.arash.shoppinglist;

import android.database.Cursor;
import android.graphics.Color;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;

public class Receivers extends AppCompatActivity {

    int TextColor_selected_int = 0xff2e8fef; //blue
    int TextColor_notSelected_int = 0xffdddddd;  //grey
    int[] ReceiversStatus_temp;
    public static int[] ReceiversStatus_static;
    public static String[] ReceiversNames_static, ReceiversIDs_static;

    int SelectedReceivers_count = 0;
    DatabaseHelper database;
    ListView receiversListView;
    Button setButton;
    ArrayList<String> receiversListItems = new ArrayList<String>();
    ArrayAdapter<String> adapter; // A STRING ADAPTER WHICH WILL HANDLE THE DATA OF THE LISTVIEW

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_receivers);

        receiversListView = (ListView)findViewById(R.id.receivers_listView);
        setButton = (Button)findViewById(R.id.setReceivers_button);
        adapter = new ArrayAdapter<String>(getApplicationContext(), R.layout.receiver_list_items, receiversListItems){
            @Override
            public View getView(int position, View convertView, ViewGroup parent) {
                View view = super.getView(position, convertView, parent);
                TextView text = (TextView) view.findViewById(R.id.receiverListView_item);
                //initialize listView texts color
                for (int i=0; i<ReceiversStatus_static.length; i++){
                    if (ReceiversStatus_static[position] == 0)
                        text.setTextColor(TextColor_notSelected_int);
                    else
                        text.setTextColor(TextColor_selected_int);
                }
                return view;
            }
        };
        receiversListView.setAdapter(adapter);

        //set "ReceiversStatus_temp"
        ReceiversStatus_temp = ReceiversStatus_static;

        //set "Set" button color
        updateSetButtonColor();

        //Show receivers listView
        database = new DatabaseHelper(this);
        displayMembersList();

        // ListView Item Click Listener
        receiversListView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                TextView clicked_item = (TextView) view.findViewById(R.id.receiverListView_item);
                // --------- set "ReceiverStatus_temp" and "SelectedReceivers_count" and update list color ---------
                if (ReceiversStatus_temp[(int)id] == 0){
                    ReceiversStatus_temp[(int)id] = 1;
                    clicked_item.setTextColor(TextColor_selected_int);}
                else if (ReceiversStatus_temp[(int)id] == 1){
                    ReceiversStatus_temp[(int)id] = 0;
                    clicked_item.setTextColor(TextColor_notSelected_int);}
                // --------- set "set" button color ---------
                updateSetButtonColor();
                // --------- get item Name ---------
                String itemValue = (String) receiversListView.getItemAtPosition(position);
            }
        });
    }

    public void setReceivers(View view){
        if (SelectedReceivers_count>0){
            //save receivers status array
            ReceiversStatus_static = ReceiversStatus_temp;
            //save receivers names
            ReceiversNames_static = new String[SelectedReceivers_count];
            ReceiversIDs_static = new String[SelectedReceivers_count];
            int ReceiversStatus_index = 0;
            int ReceiversNames_index = 0;
            Cursor res = database.getAllMembersData();
            if (res.getCount()>0){
                while (res.moveToNext()) {
                    if (ReceiversStatus_static[ReceiversStatus_index]==1) {
                        ReceiversNames_static[ReceiversNames_index] = res.getString(1);
                        ReceiversIDs_static[ReceiversNames_index] = res.getString(2);
                        ReceiversNames_index++;
                    }
                    ReceiversStatus_index++;
                }
            }

            finish();
        }
        else {
            Toast.makeText(this, "Select receivers from the list ", Toast.LENGTH_SHORT).show();
        }

    }

    public void displayMembersList() {
        Cursor res = database.getAllMembersData();
        if (res.getCount()==0){
            //show message
        }
        else{
            receiversListItems.clear();
            SelectedReceivers_count = 0;
            while (res.moveToNext()) {
                //update list of family members
                receiversListItems.add(res.getString(1)); // Add members to your array for listView
                adapter.notifyDataSetChanged(); // Check if the adapter has changed
            }
        }
    }

    public void updateSetButtonColor(){
        SelectedReceivers_count = 0;
        for (int i=0; i<ReceiversStatus_temp.length; i++)
            SelectedReceivers_count = ReceiversStatus_temp[i] + SelectedReceivers_count;
        if (SelectedReceivers_count >0){
            setButton.setBackgroundResource(R.drawable.button_simple_blue);
            setButton.setTextColor(0xffffffff); //white
        }
        else{
            setButton.setBackgroundResource(R.drawable.button_simple_grey);
            setButton.setTextColor(0xffdddddd); //grey
        }
    }

}
