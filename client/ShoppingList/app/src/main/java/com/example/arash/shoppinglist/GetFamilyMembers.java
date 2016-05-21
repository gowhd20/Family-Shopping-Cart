package com.example.arash.shoppinglist;

import android.app.ProgressDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.util.Log;
import android.widget.Toast;

import com.google.gson.Gson;
import com.google.gson.JsonObject;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

/**
 * Created by Arash on 4/28/2016.
 */
public class GetFamilyMembers extends AsyncTask<Void, Void, Void> {

    Runnable mR;
    ProgressDialog dialog;
    String res_str = "";
    final String url_for_get;
    Context context;
    DatabaseHelper database;

    public GetFamilyMembers(Context CONTEXT, String FamilyID) {
        context = CONTEXT;
        dialog = new ProgressDialog(context);
        url_for_get = "https://black-function-122210.appspot.com/ms/family/" + FamilyID + "/users/all";
    }

    @Override
    protected void onPreExecute() {
        dialog.setMessage("Processing...");
        dialog.show();
    }

    @Override
    protected void onPostExecute(Void result) {
        if (dialog.isShowing()) {
            dialog.dismiss();
        }
        UpdateLocalDatabaseMembers();
        if (MainActivity.activityTracker.equals("FamilyGroupActivity")) {
            ((FamilyGroupActivity) context).updateMembersList();
            ((FamilyGroupActivity) context).updatePanel();
        }
    }

    @Override
    protected Void doInBackground(Void... params) {
        Thread networkChecking = new Thread() {
            @Override
            public void run() {
                mR = new Runnable() {
                    @Override
                    public void run() {
                        HttpCallback cb = new HttpCallback() {
                            @Override
                            public void onFailure(Call call, IOException e) {
                                Log.d("main", "failed");
                            }

                            @Override
                            public void onSuccess(Response response) {
                                Log.d("main", "succeed");
                                try {
                                    res_str = response.body().string();
                                    Log.d("main", res_str);
                                }catch (IOException e){
                                    e.printStackTrace();
                                }

                            }
                        };

                        try {
                            res_str = getRequest(url_for_get);

                        }catch(Exception e){
                            e.printStackTrace();
                        }
                    }
                };
                mR.run();
            }
        };
        networkChecking.start();
        try {
            Thread.sleep(5000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }



        return null;
    }

    public interface HttpCallback{
        void onFailure(Call call, IOException e);

        void onSuccess(Response response);
    }

    private static final MediaType JSON = MediaType.parse("application/json; charset=utf-8");

    public String getRequest(String url) throws IOException {
        Request request;

        OkHttpClient client = new OkHttpClient();
        request = new Request.Builder()
                .url(url)
                .build();

        try {
            Response response = client.newCall(request).execute();
            String res = response.body().string();

            Log.e("main", res);
            return res;
        } catch (Exception e) {
            return null;
        }
    }

    public void UpdateLocalDatabaseMembers(){
        Log.d("main", res_str);
        JSONArray arrayObj;
        JSONObject obj, userObj;
        String userID, userName;
        database = new DatabaseHelper(context);
        database.clearFamilyMembers();

        try{
            obj = new JSONObject(res_str);
            arrayObj = obj.optJSONArray("users");
            for (int i=0; i<arrayObj.length(); i++){
                userObj = arrayObj.optJSONObject(i);
                userID = userObj.getString("uid");
                userName = userObj.getString("user_name");
                Boolean isInserted = database.insertMemberData(userName, userID);
            }
        }catch(JSONException e){
            e.printStackTrace();
            Log.d("main", "test_failed");
        }
    }

}




