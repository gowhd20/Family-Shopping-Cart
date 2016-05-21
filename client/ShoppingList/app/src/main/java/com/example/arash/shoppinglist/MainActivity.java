package com.example.arash.shoppinglist;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageView;
import android.widget.Toast;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.support.v4.content.LocalBroadcastManager;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.widget.ProgressBar;
import android.widget.TextView;

import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.GoogleApiAvailability;

public class MainActivity extends AppCompatActivity {

    private static final int PLAY_SERVICES_RESOLUTION_REQUEST = 9000;
    private static final String TAG = "MainActivity";

    private BroadcastReceiver mRegistrationBroadcastReceiver;
    private ProgressBar mRegistrationProgressBar;
    private TextView mInformationTextView;
    private boolean isReceiverRegistered;

    SharedPreferences sharedpreferences;
    static String activityTracker;
    static String googleToken_static = "";
    ImageView Me_imageView, FamilyGroup_imageView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // ----------- Google Cloud Messaging ------------
        mRegistrationBroadcastReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                SharedPreferences sharedPreferences =
                        PreferenceManager.getDefaultSharedPreferences(context);
                boolean sentToken = sharedPreferences
                        .getBoolean(QuickstartPreferences.SENT_TOKEN_TO_SERVER, false);
                Log.d("main", googleToken_static);
                if (sentToken) {
                    Log.d("main", "true");
                } else {
                    Log.d("main", "false");
                }
            }
        };
        // Registering BroadcastReceiver
        registerReceiver();
        if (checkPlayServices()) {
            // Start IntentService to register this application with GCM.
            Intent intent = new Intent(this, RegistrationIntentService.class);
            startService(intent);
        }
        Log.d("main", googleToken_static);
        // -----------------------------------------------

        Me_imageView = (ImageView)findViewById(R.id.me_icon);
        FamilyGroup_imageView = (ImageView)findViewById(R.id.FamilyGroup_icon);

        // Load saved UserName, joinStatus, familyName, userID and familyID
        sharedpreferences = getSharedPreferences("preferences", Context.MODE_PRIVATE);
        if (sharedpreferences.contains("user_name"))
            MeActivity.UserName_static = sharedpreferences.getString("user_name", "-");
        else
            MeActivity.UserName_static = "-";
        if (sharedpreferences.contains("join_status"))
            FamilyGroupActivity.JoinStatus_static = sharedpreferences.getBoolean("join_status", false);
        else
            FamilyGroupActivity.JoinStatus_static = false;
        if (sharedpreferences.contains("family_id"))
            FamilyGroupActivity.familyID_static = sharedpreferences.getString("family_id", "");
        else
            FamilyGroupActivity.familyID_static = "";
        if (sharedpreferences.contains("family_name"))
            FamilyGroupActivity.familyName_static = sharedpreferences.getString("family_name", "");
        else
            FamilyGroupActivity.familyName_static = "";
        if (sharedpreferences.contains("user_id"))
            FamilyGroupActivity.userID_static = sharedpreferences.getString("user_id", "");
        else
            FamilyGroupActivity.userID_static = "";

        if (FamilyGroupActivity.JoinStatus_static == true) {
            // updateFamilyMembersLocalDatabase
            GetFamilyMembers getFamilyMembers = new GetFamilyMembers(this, FamilyGroupActivity.familyID_static);
            getFamilyMembers.execute();
            // updateShoppingCartDatabase
            GetShoppingCart getShoppingCart = new GetShoppingCart(this, FamilyGroupActivity.familyID_static);
            getShoppingCart.execute();
        }

    }



    public void OpenShoppingListPage(View V){
        if (FamilyGroupActivity.JoinStatus_static == true){
            Intent intent = new Intent(this, ShoppingListActivity.class);
            startActivity(intent);
        }else {
            Toast.makeText(MainActivity.this, "Please join a family to access", Toast.LENGTH_SHORT).show();
            FamilyGroup_imageView.setImageResource(R.drawable.home_page_group_orange);
        }

    }

    public void OpenFamilyGroupPage(View V){
        if (MeActivity.UserName_static.equals("-")) {
            Toast.makeText(MainActivity.this, "Please first assign a user name for yourself", Toast.LENGTH_SHORT).show();
            Me_imageView.setImageResource(R.drawable.home_page_me_orange);
        }else{
            Intent intent = new Intent(this, FamilyGroupActivity.class);
            startActivity(intent);
        }
    }

    public void OpenMePage(View V){
        Intent intent = new Intent(this, MeActivity.class);
        startActivity(intent);
    }

    @Override
    protected void onResume() {
        super.onResume();
        registerReceiver();

        activityTracker = "MainActivity";
        if (!(MeActivity.UserName_static.equals("-")))
            Me_imageView.setImageResource(R.drawable.home_page_me);
        if (FamilyGroupActivity.JoinStatus_static == true)
            FamilyGroup_imageView.setImageResource(R.drawable.home_page_group);
    }

    @Override
    protected void onPause() {
        LocalBroadcastManager.getInstance(this).unregisterReceiver(mRegistrationBroadcastReceiver);
        isReceiverRegistered = false;
        super.onPause();
    }

    private void registerReceiver() {
        if (!isReceiverRegistered) {
            LocalBroadcastManager.getInstance(this).registerReceiver(mRegistrationBroadcastReceiver,
                    new IntentFilter(QuickstartPreferences.REGISTRATION_COMPLETE));
            isReceiverRegistered = true;
        }
    }

    /**
     * Check the device to make sure it has the Google Play Services APK. If
     * it doesn't, display a dialog that allows users to download the APK from
     * the Google Play Store or enable it in the device's system settings.
     */
    private boolean checkPlayServices() {
        GoogleApiAvailability apiAvailability = GoogleApiAvailability.getInstance();
        int resultCode = apiAvailability.isGooglePlayServicesAvailable(this);
        if (resultCode != ConnectionResult.SUCCESS) {
            if (apiAvailability.isUserResolvableError(resultCode)) {
                apiAvailability.getErrorDialog(this, resultCode, PLAY_SERVICES_RESOLUTION_REQUEST)
                        .show();
            } else {
                Log.i(TAG, "This device is not supported.");
                finish();
            }
            return false;
        }
        return true;
    }
}
