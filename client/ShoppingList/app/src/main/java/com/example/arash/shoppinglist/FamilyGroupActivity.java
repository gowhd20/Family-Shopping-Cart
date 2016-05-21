package com.example.arash.shoppinglist;

import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.graphics.Color;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;

public class FamilyGroupActivity extends AppCompatActivity {

    DeviceInfo myDevice;
    static String macAddress;
    DatabaseHelper database;
    EditText editName;
    ListView membersListView;
    ImageView JoinExitButton, CreateButton, usersIcon, familyTitleImage;
    ArrayList<String> membersListItems = new ArrayList<String>();
    ArrayAdapter<String> adapter; // A STRING ADAPTER WHICH WILL HANDLE THE DATA OF THE LISTVIEW
    int SelectedFamilyGroupItemPosition = -1;
    static String familyID_static, familyName_static, userID_static;
    static Boolean JoinStatus_static;
    Boolean familyNameIsInserted;
    SharedPreferences sharedpreferences;
    TextView familyTitle_textView;
    String familyName_join, familyID_join;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_family_group);

        editName = (EditText)findViewById(R.id.Name_editText);
        JoinExitButton = (ImageView)findViewById(R.id.RemoveMember_icon);
        CreateButton = (ImageView)findViewById(R.id.AddMember_icon);
        familyTitleImage = (ImageView)findViewById(R.id.FamilyGroupTitleImage_ImageView);
        familyTitle_textView = (TextView)findViewById(R.id.FamilyGroupTitle_TextView);
        usersIcon = (ImageView)findViewById(R.id.FamilyGroupPlus_ImageView);
        database = new DatabaseHelper(this);
        membersListView = (ListView)findViewById(R.id.Members_listView);
        adapter = new ArrayAdapter<String>(getApplicationContext(), R.layout.family_members_items, membersListItems) {
            @Override
            public View getView(int position, View convertView, ViewGroup parent) {
                View view = super.getView(position, convertView, parent);
                TextView text = (TextView) view.findViewById(R.id.receiverListView_item);
                //initialize listView background
                if (SelectedFamilyGroupItemPosition >= 0){
                    if (SelectedFamilyGroupItemPosition == position)
                        view.setBackgroundResource(R.drawable.shopping_list_background_selected);
                    else
                        view.setBackgroundResource(R.drawable.shopping_list_background_normal);
                }
                return view;
            }
        };
        membersListView.setAdapter(adapter);

        familyNameIsInserted = false;

        // Load joinStatus, familyName, userID and familyID
        sharedpreferences = getSharedPreferences("preferences", Context.MODE_PRIVATE);
        if (sharedpreferences.contains("join_status"))
            JoinStatus_static = sharedpreferences.getBoolean("join_status", false);
        else
            JoinStatus_static = false;
        if (sharedpreferences.contains("family_id"))
            familyID_static = sharedpreferences.getString("family_id", "");
        else
            familyID_static = "";
        if (sharedpreferences.contains("family_name"))
            familyName_static = sharedpreferences.getString("family_name", "");
        else
            familyName_static = "";
        if (sharedpreferences.contains("user_id"))
            userID_static = sharedpreferences.getString("user_id", "");
        else
            userID_static = "";

        //get MAC address
        myDevice = new DeviceInfo();
        macAddress = myDevice.getMacAddress(this);

        //update panel (buttons, title and so on)
        updatePanel();

        //update member list
        updateMembersList();

        //Track EditText to find out something is entered in or not
        editName.addTextChangedListener(new TextWatcher() {
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {
            }

            public void onTextChanged(CharSequence s, int start, int before, int count) {
            }

            @Override
            public void afterTextChanged(Editable s) {
                if (String.valueOf(s).equals("")) {
                    usersIcon.setImageResource(R.drawable.users_icon_white);
                    CreateButton.setImageResource(R.drawable.family_create_grey);
                    JoinExitButton.setImageResource(R.drawable.family_join_grey);
                } else {
                    usersIcon.setImageResource(R.drawable.plus_empty);
                    CreateButton.setImageResource(R.drawable.family_create_blue);
                    JoinExitButton.setImageResource(R.drawable.family_join_blue);
                }
            }
        });

    }
    
    public void CreateFamily_button(View V){
        if (editName.getText().toString().equals("")){
            Toast.makeText(this, "Please insert family's name.", Toast.LENGTH_SHORT).show();
        }
        else{
            String url = "https://black-function-122210.appspot.com/ms/family";
            String familyName = editName.getText().toString();
            String MAC = "mac_fake_sahba_1";
            String token = "gt_fake_sahba_1";
            String userName = MeActivity.UserName_static;
            CreateFamily createFamily = new CreateFamily(this, url, familyName, MAC, userName, token);
            createFamily.execute();
        }
    }

    public void JoinOrExitFamily(View V){
        if (JoinStatus_static == false){

            if (familyNameIsInserted == false) {
                if (editName.getText().toString().equals(""))
                    Toast.makeText(this, "Please insert family name.", Toast.LENGTH_SHORT).show();
                else {
                    familyNameIsInserted = true;
                    familyName_join = editName.getText().toString();
                    editName.setText("");
                    editName.setHint("Family Id");
                    usersIcon.setImageResource(R.drawable.lock_white);}
            }
            else{
                if (editName.getText().toString().equals(""))
                    Toast.makeText(this, "Please insert family ID.", Toast.LENGTH_SHORT).show();
                else {
                    familyNameIsInserted = true;
                    String MAC = "fake_macAddress_3";
                    String token = MainActivity.googleToken_static;
                    String userName = MeActivity.UserName_static;
                    familyID_join = editName.getText().toString();
                    String url = "https://black-function-122210.appspot.com/ms/family/"+ familyName_join+"/users";
                    JoinFamily joinFamily = new JoinFamily(this, url, familyName_join, familyID_join, MAC, userName, token);
                    joinFamily.execute();
                    familyNameIsInserted = true;
                }
            }
        }
        else {
            ExitFromFamily();
        }
    }

    public void  ExitFromFamily(){
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder
                .setTitle("Exit from family !")
                .setMessage(" Are you sure?")
                .setIcon(android.R.drawable.ic_dialog_alert)
                .setPositiveButton("Yes", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        //Exit from family
                        ExitFamily exitFamily = new ExitFamily(FamilyGroupActivity.this);
                        exitFamily.execute();
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

    public void updateFamilyMembersLocalDatabase(){
        if (JoinStatus_static == true) {
            GetFamilyMembers getFamilyMembers = new GetFamilyMembers(this, familyID_static);
            getFamilyMembers.execute();
        }
    }

    public void updateMembersList(){
        Cursor res = database.getAllMembersData();
        if (res.getCount()==0){
            membersListItems.clear();
            adapter.notifyDataSetChanged(); // Check if the adapter has changed
        }
        else{
            membersListItems.clear();
            while (res.moveToNext()) {
                //update list of family members
                membersListItems.add(res.getString(1)); // Add members to your array for listView
                adapter.notifyDataSetChanged(); // Check if the adapter has changed
            }
        }
    }

    public void updatePanel(){
        if (JoinStatus_static == true ){
            editName.setText("");
            editName.setHint("Family Members");
            editName.setEnabled(false);
            editName.setBackgroundResource(R.drawable.family_group_edit_text_join);
            JoinExitButton.setImageResource(R.drawable.family_exit_red);
            CreateButton.setImageResource(R.drawable.plus_empty);
            familyTitleImage.setImageResource(R.drawable.users);
            familyTitle_textView.setBackgroundResource(R.drawable.shopping_list_title_background);
            familyTitle_textView.setText("      " + familyName_static);
            usersIcon.setImageResource(R.drawable.users_icon_white);
        }
        else{
            editName.setHint("Family Name");
            editName.setEnabled(true);
            editName.setBackgroundResource(R.drawable.family_group_edit_text_not_join);
            JoinExitButton.setImageResource(R.drawable.family_join_grey);
            CreateButton.setImageResource(R.drawable.family_create_grey);
            familyTitleImage.setImageResource(R.drawable.users_grey);
            familyTitle_textView.setBackgroundResource(R.drawable.shopping_list_title_background_grey);
            familyTitle_textView.setText("      Family Group");
            usersIcon.setImageResource(R.drawable.users_icon_white);
            database.clearFamilyMembers();
        }

    }

    public  void ShowFamilyID(View view){
        Toast.makeText(FamilyGroupActivity.this, familyID_static, Toast.LENGTH_LONG).show();
    }

    @Override
    protected void onResume() {
        super.onResume();
        MainActivity.activityTracker = "FamilyGroupActivity";

        SelectedFamilyGroupItemPosition = -1;
        //update member list
        updateMembersList();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();

        // Save JoinStatus
        SharedPreferences.Editor editor = sharedpreferences.edit();
        editor.putBoolean("join_status", JoinStatus_static);
        editor.putString("family_id", familyID_static);
        editor.putString("family_name", familyName_static);
        editor.putString("user_id", userID_static);
        editor.commit();
    }
}
