package com.example.arash.shoppinglist;

import android.app.Dialog;
import android.app.TimePickerDialog;
import android.content.ClipData;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Color;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.TimePicker;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.Calendar;

public class AddItem extends AppCompatActivity {

    DatabaseHelper database;
    TextView ItemName_textView, ItemTime_textView, ItemReceivers_textView;
    CheckBox urgencyCheckbox;
    Button NeedTimeButton;
    EditText ItemNameEditText, ItemPriceEditText, ItemPlaceEditText, ItemDescriptionEditText;
    ImageView AddToCart_button;
    final Calendar calendar = Calendar.getInstance();
    int currentHour, currentMinute, needHour, needMinute, UrgencyValue;
    static final int TIME_PICKER_DIALOG_ID = 0;
    // A valid item should have at least 'Name' and 'Time of the need' and 'Receivers'
    boolean itemNameIsSet = false;
    boolean itemReceiversIsSet = false;
    boolean itemNeedTimeIsSet = false;
    boolean itemIsValid = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_add_item);

        database = new DatabaseHelper(this);
        ItemName_textView = (TextView)findViewById(R.id.itemName_textView);
        ItemTime_textView =(TextView)findViewById(R.id.time_textView);
        ItemReceivers_textView = (TextView)findViewById(R.id.receivers_textView);
        urgencyCheckbox = (CheckBox)findViewById(R.id.itemUrgency_checkbox);
        NeedTimeButton = (Button)findViewById(R.id.itemTime_button);
        AddToCart_button = (ImageView)findViewById(R.id.itemAdd_button);
        ItemNameEditText = (EditText)findViewById(R.id.itemName_editText);
        ItemPriceEditText = (EditText)findViewById(R.id.itemPrice_editText);
        ItemPlaceEditText = (EditText)findViewById(R.id.itemPlace_editText);
        ItemDescriptionEditText = (EditText)findViewById(R.id.itemDescription_editText);

        setDefaultValues();

        //Track item name to find out something is entered in or not
        ItemNameEditText.addTextChangedListener(new TextWatcher() {
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            public void onTextChanged(CharSequence s, int start, int before, int count) {}

            @Override
            public void afterTextChanged(Editable s) {
                if (String.valueOf(s).equals("")) {
                    itemNameIsSet = false;
                    itemIsValid = false;
                    AddToCart_button.setImageResource(R.drawable.create_grey);
                }
                else{
                    itemNameIsSet = true;
                    ItemName_textView.setTextColor(Color.BLACK);
                    if (itemNeedTimeIsSet && itemReceiversIsSet) {
                        itemIsValid = true;
                        AddToCart_button.setImageResource(R.drawable.create_blue);
                    }
                }
            }
        });
    }

    public void setDefaultValues() {
        // set "Time of the need" to current time
        String currentHour_str, currentMin_str;
        currentHour = calendar.get(Calendar.HOUR_OF_DAY);
        currentMinute = calendar.get(Calendar.MINUTE);
        if (currentHour < 10)
            currentHour_str = "0" + String.valueOf(currentHour);
        else
            currentHour_str = String.valueOf(currentHour);
        if (currentMinute < 10)
            currentMin_str = "0" + String.valueOf(currentMinute);
        else
            currentMin_str = String.valueOf(currentMinute);
        NeedTimeButton.setText(currentHour_str + ":" + currentMin_str);
        // set time background to grey
        NeedTimeButton.setBackgroundResource(R.drawable.button_simple_grey);

        // initialize "ReceiversStatus_static"
        DatabaseHelper database = new DatabaseHelper(this);
        Cursor res = database.getAllMembersData();
        Receivers.ReceiversStatus_static = new int[res.getCount()];
        for (int i = 0; i < res.getCount(); i++) {
            Receivers.ReceiversStatus_static[i] = 0;
        }

    }

    public Boolean addItem(View view){
        // Check if necessary data has been entered
        if (itemIsValid){
            // if necessary data entered do save process and exit. (to TABLE_newItems)
            boolean isInserted;
            String itemName = ItemNameEditText.getText().toString();
            String itemPrice = ItemPriceEditText.getText().toString();
            String itemPlace = ItemPlaceEditText.getText().toString();
            // join receivers name together as a string
            String[] receivers_dummy = Receivers.ReceiversNames_static;
            String receiversName = TextUtils.join(", ", receivers_dummy);     // name1 , name2 , ...
            // join receivers name together as a string
            receivers_dummy = Receivers.ReceiversIDs_static;
            String receiversID = TextUtils.join(", ", receivers_dummy);     // uid1 , uid2 , ...
            String itemDescription = ItemDescriptionEditText.getText().toString();
            if (urgencyCheckbox.isChecked())
                UrgencyValue = 1;
            else
                UrgencyValue = 0;

            isInserted = database.insertNewItemData(itemName, needHour, needMinute, UrgencyValue, itemPrice, itemPlace, receiversName, itemDescription, receiversID);

            finish();
        }
        else{
            // display a toast as an error and change unfilled item to red
            if (itemNameIsSet==false)
                ItemName_textView.setTextColor(Color.RED);
            if (itemNeedTimeIsSet == false)
                ItemTime_textView.setTextColor(Color.RED);
            if (itemReceiversIsSet == false)
                ItemReceivers_textView.setTextColor(Color.RED);

            if(itemNameIsSet && itemNeedTimeIsSet && itemReceiversIsSet==false)
                Toast.makeText(AddItem.this, " Please set:\n       Receivers", Toast.LENGTH_SHORT).show();
            if(itemNameIsSet && itemNeedTimeIsSet==false && itemReceiversIsSet)
                Toast.makeText(AddItem.this, " Please set:\n       Time of need", Toast.LENGTH_SHORT).show();
            if(itemNameIsSet==false && itemNeedTimeIsSet && itemReceiversIsSet)
                Toast.makeText(AddItem.this, " Please set:\n       Item name", Toast.LENGTH_SHORT).show();
            if(itemNameIsSet && itemNeedTimeIsSet==false && itemReceiversIsSet==false)
                Toast.makeText(AddItem.this, " Please set:\n       Time of need\n       Receivers", Toast.LENGTH_SHORT).show();
            if(itemNameIsSet==false && itemNeedTimeIsSet && itemReceiversIsSet==false)
                Toast.makeText(AddItem.this, " Please set:\n       Item name\n       Receivers", Toast.LENGTH_SHORT).show();
            if(itemNameIsSet==false && itemNeedTimeIsSet==false && itemReceiversIsSet)
                Toast.makeText(AddItem.this, " Please set:\n       Item name\n       Time of need", Toast.LENGTH_SHORT).show();
            if(itemNameIsSet==false && itemNeedTimeIsSet==false && itemReceiversIsSet==false)
                Toast.makeText(AddItem.this, " Please set:\n       Item name\n       Time of need\n" +
                        "       Receivers", Toast.LENGTH_SHORT).show();
        }
        return true;
    }

    public void toWhom(View view){
        Intent intent = new Intent(this, Receivers.class);
        startActivity(intent);
    }

    //---------------------------------- TimePicker ----------------------------------
    public void pickTimeOfNeed(View view){
        showDialog(TIME_PICKER_DIALOG_ID);
    }

    @Override
    protected Dialog onCreateDialog(int id){
        if (id == TIME_PICKER_DIALOG_ID)
            return new TimePickerDialog(AddItem.this, timePickerListener, needHour, needMinute, true);
        else
            return null;
    }

    protected TimePickerDialog.OnTimeSetListener timePickerListener =
            new TimePickerDialog.OnTimeSetListener() {
                @Override
                public void onTimeSet(TimePicker view, int hourOfDay, int minute) {
                    String needHour_str, needMinute_str;
                    needHour = hourOfDay;
                    needMinute = minute;

                    if (needHour<10)
                        needHour_str = "0" + String.valueOf(needHour);
                    else
                        needHour_str = String.valueOf(needHour);
                    if (needMinute<10)
                        needMinute_str = "0" + String.valueOf(needMinute);
                    else
                        needMinute_str = String.valueOf(needMinute);

                    NeedTimeButton.setText(needHour_str + ":" + needMinute_str);
                    NeedTimeButton.setBackgroundResource(R.drawable.button_simple_blue);
                    itemNeedTimeIsSet = true;
                    if (itemNameIsSet && itemReceiversIsSet)
                        AddToCart_button.setImageResource(R.drawable.create_blue);
                    ItemTime_textView.setTextColor(Color.BLACK);
                }
            };
    //------------------------------- End of TimePicker -------------------------------


    @Override
    protected void onResume() {
        super.onResume();
        //update Receivers icon
        ImageView receiversIcon = (ImageView)findViewById(R.id.toWhom_icon);
        int receivers_count = 0;
        for (int i=0; i<Receivers.ReceiversStatus_static.length; i++) {
            if (Receivers.ReceiversStatus_static[i] == 1)
            receivers_count++;
        }
        if (receivers_count == 0){
            receiversIcon.setImageResource(R.drawable.whom_icon_not_selected);
            itemReceiversIsSet = false;
            itemIsValid =false;
            AddToCart_button.setImageResource(R.drawable.create_grey);
        }
        else {
            receiversIcon.setImageResource(R.drawable.whom_icon_selected);
            ItemReceivers_textView.setTextColor(Color.BLACK);
            itemReceiversIsSet = true;
            if (itemNameIsSet && itemNeedTimeIsSet){
                itemIsValid = true;
                AddToCart_button.setImageResource(R.drawable.create_blue);
            }
        }
    }
}
