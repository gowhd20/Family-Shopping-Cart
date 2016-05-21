package com.example.arash.shoppinglist;

import android.content.Context;
import android.content.SharedPreferences;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.Editable;
import android.text.InputType;
import android.text.TextWatcher;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.Toast;

public class MeActivity extends AppCompatActivity {

    EditText userName_editText;
    ImageView userNameSave_imageView;
    static String UserName_static;
    SharedPreferences sharedpreferences;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_me);

        userName_editText = (EditText)findViewById(R.id.UserName_editText);
        userName_editText.setEnabled(false);
        userNameSave_imageView = (ImageView)findViewById(R.id.UserNameSave_imageView);

        // Load saved UserName
        sharedpreferences = getSharedPreferences("preferences", Context.MODE_PRIVATE);
        if (sharedpreferences.contains("user_name"))
            UserName_static = sharedpreferences.getString("user_name", "-");
        else
            UserName_static = "-";
        userName_editText.setText(UserName_static);



        //Track to find out something is entered in or not
        userName_editText.addTextChangedListener(new TextWatcher() {
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            public void onTextChanged(CharSequence s, int start, int before, int count) {}

            @Override
            public void afterTextChanged(Editable s) {
                if (!String.valueOf(s).equals(UserName_static)) {
                    userNameSave_imageView.setImageResource(R.drawable.save_white);
                }
            }
        });


    }

    public  void UserNameEdit(View view){
        if (FamilyGroupActivity.JoinStatus_static == false)
            userName_editText.setEnabled(true);
        else
            Toast.makeText(MeActivity.this, "You already joined a Family using this name.\nIt could not be changed until you are joined to the family.", Toast.LENGTH_LONG).show();
    }
    
    public void UserNameSave(View view){

        if (userName_editText.getText().toString().equals("")){
            Toast.makeText(MeActivity.this, "Name is Invalid !", Toast.LENGTH_SHORT).show();
        }
        else{
            UserName_static = userName_editText.getText().toString();
            SharedPreferences.Editor editor = sharedpreferences.edit();
            editor.putString("user_name", UserName_static);
            editor.commit();
            userNameSave_imageView.setImageResource(R.drawable.plus_empty);
            userName_editText.setEnabled(false);
        }
    }
}
