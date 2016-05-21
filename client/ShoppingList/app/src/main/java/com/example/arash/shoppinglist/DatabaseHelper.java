package com.example.arash.shoppinglist;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

/**
 * Created by Arash on 4/9/2016.
 */
public class DatabaseHelper extends SQLiteOpenHelper {

    public static final String DATABASE_NAME = "FamilyShoppingCart.db";

    // Family members table
    public static final String TABLE_MEMBERS = "FamilyMembers_table";
    public static final String TABLE_MEMBERS_COL_1 = "ID";
    public static final String TABLE_MEMBERS_COL_2 = "NAME";
    public static final String TABLE_MEMBERS_COL_3 = "UID";

    // Shopping Items table
    public static final String TABLE_Items = "ShoppingItems_table";
    public static final String TABLE_Items_COL_1 = "ID";
    public static final String TABLE_Items_COL_2 = "itemName";
    public static final String TABLE_Items_COL_3= "itemTimeHour";
    public static final String TABLE_Items_COL_4 = "itemTimeMinute";
    public static final String TABLE_Items_COL_5 = "itemUrgency";
    public static final String TABLE_Items_COL_6 = "itemPrice";
    public static final String TABLE_Items_COL_7 = "itemPlace";
    public static final String TABLE_Items_COL_8 = "itemReceiversName";
    public static final String TABLE_Items_COL_9 = "itemWhoBuy";
    public static final String TABLE_Items_COL_10 = "itemWhoAsked";
    public static final String TABLE_Items_COL_11 = "itemDescription";
    public static final String TABLE_Items_COL_12 = "itemID";
    public static final String TABLE_Items_COL_13 = "itemReceiversID";


    // New Shopping Items table
    public static final String TABLE_newItems = "ShoppingNewItems_table";
    public static final String TABLE_newItems_COL_1 = "newItemID";
    public static final String TABLE_newItems_COL_2 = "newItemName";
    public static final String TABLE_newItems_COL_3= "newItemTimeHour";
    public static final String TABLE_newItems_COL_4 = "newItemTimeMinute";
    public static final String TABLE_newItems_COL_5 = "newItemUrgency";
    public static final String TABLE_newItems_COL_6 = "newItemPrice";
    public static final String TABLE_newItems_COL_7 = "newItemPlace";
    public static final String TABLE_newItems_COL_8 = "newItemReceivers";
    public static final String TABLE_newItems_COL_9 = "newItemDescription";
    public static final String TABLE_newItems_COL_10 = "newItemReceiversID";


    public DatabaseHelper(Context context) {
        super(context, DATABASE_NAME, null, 1);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL("create table " + TABLE_MEMBERS + " (ID INTEGER PRIMARY KEY AUTOINCREMENT, NAME TEXT, UID TEXT)");
        db.execSQL("create table " + TABLE_Items + " (ID INTEGER PRIMARY KEY AUTOINCREMENT, itemName TEXT, itemTimeHour INTEGER, itemTimeMinute INTEGER, itemUrgency INTEGER, itemPrice TEXT, itemPlace TEXT, itemReceiversName TEXT, itemWhoBuy TEXT, itemWhoAsked TEXT, itemDescription TEXT, itemID TEXT, itemReceiversID TEXT)");
        db.execSQL("create table " + TABLE_newItems + " (newItemID INTEGER PRIMARY KEY AUTOINCREMENT, newItemName TEXT, newItemTimeHour INTEGER, newItemTimeMinute INTEGER, newItemUrgency INTEGER, newItemPrice TEXT, newItemPlace TEXT, newItemReceivers TEXT, newItemDescription TEXT, newItemReceiversID TEXT)");
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_MEMBERS);
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_Items);
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_newItems);

        // create new tables
        onCreate(db);
    }

    // (start) ------------- FamilyMembers_table Functions -------------
    public boolean insertMemberData(String name, String uid){
        SQLiteDatabase db = this.getReadableDatabase();
        ContentValues contentValues = new ContentValues();
        contentValues.put(TABLE_MEMBERS_COL_2, name);
        contentValues.put(TABLE_MEMBERS_COL_3, uid);
        long result = db.insert(TABLE_MEMBERS, null, contentValues);
        if (result == -1)
            return false;
        else
            return true;
    }
    public Cursor getAllMembersData(){
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor res = db.rawQuery("select * from " + TABLE_MEMBERS, null);
        return res;
    }
    public Integer removeMember(String name){
        SQLiteDatabase db = this.getReadableDatabase();
        return db.delete(TABLE_MEMBERS, "NAME = ?", new String[] {name});
    }
    public void clearFamilyMembers(){
        SQLiteDatabase db = this.getReadableDatabase();
        db.delete(TABLE_MEMBERS,null,null);
    }
    // (end) ------------- FamilyMembers_table Functions -------------

    // (start) ------------- ShoppingItems_table Functions -------------
    public boolean insertItemData(String itemName, int itemTime_hour, int itemTime_minute, int itemUrgency, String itemPrice, String itemPlace, String itemReceivers, String itemWhoBuy, String itemWhoAsked, String itemDescription, String itemID, String itemReceiversID){
        SQLiteDatabase db = this.getReadableDatabase();
        ContentValues contentValues = new ContentValues();
        contentValues.put(TABLE_Items_COL_2, itemName);
        contentValues.put(TABLE_Items_COL_3, itemTime_hour);
        contentValues.put(TABLE_Items_COL_4, itemTime_minute);
        contentValues.put(TABLE_Items_COL_5, itemUrgency);
        contentValues.put(TABLE_Items_COL_6, itemPrice);
        contentValues.put(TABLE_Items_COL_7, itemPlace);
        contentValues.put(TABLE_Items_COL_8, itemReceivers);
        contentValues.put(TABLE_Items_COL_9, itemWhoBuy);
        contentValues.put(TABLE_Items_COL_10, itemWhoAsked);
        contentValues.put(TABLE_Items_COL_11, itemDescription);
        contentValues.put(TABLE_Items_COL_12, itemID);
        contentValues.put(TABLE_Items_COL_13, itemReceiversID);
        long result = db.insert(TABLE_Items, null, contentValues);
        if (result == -1)
            return false;
        else
            return true;
    }
    public Cursor getAllItemData(){
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor res = db.rawQuery("select * from " + TABLE_Items, null);
        return res;
    }
    public Integer removeItem(String name){
        SQLiteDatabase db = this.getReadableDatabase();
        return db.delete(TABLE_Items, "itemName = ?", new String[] {name});
    }
    public void clearShoppingListItems(){
        SQLiteDatabase db = this.getReadableDatabase();
        db.delete(TABLE_Items,null,null);
    }
    // (end) ------------- ShoppingItems_table Functions -------------

    // (start) ------------- ShoppingNewItems_table Functions -------------
    public boolean insertNewItemData(String itemName, int itemTime_hour, int itemTime_minute, int itemUrgency, String itemPrice, String itemPlace, String itemReceivers,String itemDescription, String itemReceiversID){
        SQLiteDatabase db = this.getReadableDatabase();
        ContentValues contentValues = new ContentValues();
        contentValues.put(TABLE_newItems_COL_2, itemName);
        contentValues.put(TABLE_newItems_COL_3, itemTime_hour);
        contentValues.put(TABLE_newItems_COL_4, itemTime_minute);
        contentValues.put(TABLE_newItems_COL_5, itemUrgency);
        contentValues.put(TABLE_newItems_COL_6, itemPrice);
        contentValues.put(TABLE_newItems_COL_7, itemPlace);
        contentValues.put(TABLE_newItems_COL_8, itemReceivers);
        contentValues.put(TABLE_newItems_COL_9, itemDescription);
        contentValues.put(TABLE_newItems_COL_10, itemReceiversID);
        long result = db.insert(TABLE_newItems, null, contentValues);
        if (result == -1)
            return false;
        else
            return true;
    }
    public Cursor getAllNewItemData(){
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor res = db.rawQuery("select * from " + TABLE_newItems, null);
        return res;
    }
    public Integer removeNewItem(String name){
        SQLiteDatabase db = this.getReadableDatabase();
        return db.delete(TABLE_newItems, "newItemName = ?", new String[] {name});
    }
    public void clearNewItems(){
        SQLiteDatabase db = this.getReadableDatabase();
        db.delete(TABLE_newItems,null,null);
    }
    // (end) ------------- ShoppingNewItems_table Functions -------------
}
