package com.example.arash.shoppinglist;

import android.content.Context;
import android.net.wifi.WifiManager;

/**
 * Created by Arash on 4/28/2016.
 */
public class DeviceInfo {
    public String getMacAddress(Context context) {
        WifiManager wifiManager = (WifiManager) context.getSystemService(Context.WIFI_SERVICE);
        String macAddress = wifiManager.getConnectionInfo().getMacAddress();
        if (macAddress == null) {
            macAddress = "Device doesn't have mac address or wi-fi is disabled";
        }
        return macAddress;
    }

}
