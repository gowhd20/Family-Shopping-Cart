package com.example.arash.shoppinglist;

import android.app.ProgressDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.os.AsyncTask;
import android.text.TextUtils;
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
public class GetShoppingCart extends AsyncTask<Void, Void, Void> {

    Runnable mR;
    ProgressDialog dialog;
    String res_str = "";
    final String url_for_get;
    Context context;
    DatabaseHelper database;

    public GetShoppingCart(Context CONTEXT, String FamilyID) {
        context = CONTEXT;
        dialog = new ProgressDialog(context);
        url_for_get = "https://black-function-122210.appspot.com/ms/family/" + FamilyID + "/requests";
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
        UpdateLocalDatabaseShoppingItems();
        if (MainActivity.activityTracker.equals("ShoppingListActivity")) { // after add new items
            database = new DatabaseHelper(context);
            database.clearNewItems();
            ((ShoppingListActivity) context).updateShoppingList();
            ((ShoppingListActivity) context).updateNewItemsPanel();
        }

        if (MainActivity.activityTracker.equals("DetailsItemActivity")) //after delete an item
                ((DetailsItemActivity)context).finish();
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

    public void UpdateLocalDatabaseShoppingItems(){
        Log.d("main", res_str);
        JSONArray arrayObj, innerObjArray;
        JSONObject obj, itemObj, innerObj;
        database = new DatabaseHelper(context);
        database.clearShoppingListItems();
        String itemName;
        String itemID;
        int itemTimeHour;
        int itemTimeMin;
        int itemUrgency;
        String itemPrice;
        String itemPlace;
        String receiversName_str, receiversID_str, acceptors_str = "";
        String[] receiversName_array, receiversID_array, acceptors_array;
        String itemSenderName = "", itemSenderID;
        String itemDescription;
        String receiverID;

        try{

            obj = new JSONObject(res_str);
            arrayObj = obj.optJSONArray("requests");
            for (int i=0; i<arrayObj.length(); i++){
                itemObj = arrayObj.optJSONObject(i);
                itemDescription = itemObj.getString("description");
                //receivers names and IDs
                innerObjArray = itemObj.optJSONArray("receivers");
                receiversName_array = new String[innerObjArray.length()];
                receiversID_array = new String[innerObjArray.length()];
                for (int j=0; j<innerObjArray.length(); j++){
                    innerObj = innerObjArray.optJSONObject(j);
                    receiverID = innerObj.getString("uid");
                    receiversID_array[j] = receiverID;
                    Cursor res = database.getAllMembersData();
                    while (res.moveToNext()) {
                        if (res.getString(2).equals(receiverID))
                            receiversName_array[j] = res.getString(1);
                    }
                }
                receiversName_str = TextUtils.join(", ", receiversName_array);
                receiversID_str = TextUtils.join(", ", receiversID_array);
                itemPrice = itemObj.getString("price");
                itemID = itemObj.getString("req_uuid");
                innerObj = itemObj.optJSONObject("sender");
                itemSenderID = innerObj.getString("uid");
                Cursor res = database.getAllMembersData();
                while (res.moveToNext()) {
                    if (res.getString(2).equals(itemSenderID))
                        itemSenderName = res.getString(1);
                }
                itemName = itemObj.getString("item");
                // This approach is better to be replaced with Unix (epoch) time, But for that date of need also is needed.
                int timeNeed = itemObj.getInt("time_of_need");
                itemTimeHour = timeNeed / 100;
                itemTimeMin = timeNeed % 100;
                itemPlace = itemObj.getString("location");
                itemUrgency = itemObj.getInt("urgency");
                if (itemObj.has("acceptors")){
                    innerObjArray = itemObj.optJSONArray("acceptors");
                    acceptors_str = "";
                    acceptors_array = new String[innerObjArray.length()];
                    for (int j=0; j<innerObjArray.length(); j++){
                        innerObj = innerObjArray.optJSONObject(j);
                        String acceptorID = innerObj.getString("uid");
                        res = database.getAllMembersData();
                        while (res.moveToNext()) {
                            if (res.getString(2).equals(acceptorID))
                                acceptors_array[j] = res.getString(1);
                        }
                        acceptors_str = TextUtils.join(", ", acceptors_array);
                    }
                }
                Boolean isInserted = database.insertItemData(itemName,itemTimeHour,itemTimeMin,itemUrgency,itemPrice,itemPlace,receiversName_str,acceptors_str,itemSenderName,itemDescription,itemID,receiversID_str);
            }
        }catch(JSONException e){
            e.printStackTrace();
            Log.d("main", "test_failed");
        }
    }

}




