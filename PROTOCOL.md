# Yeelock BT protocol

Based on information from [this topic](https://community.home-assistant.io/t/xiaomi-mijia-yeelock-integration/92331) and other sources, I was able to discover following flow:

1. Offical (smartphone) app connects to server to fetch list of the locks and BT sign keys  
   It seems that app does not store sign key because it won't work without internet connection, and
   to allow the possibility of revoking the rights to the shared lock.
2. When trying to interact with lock, app will seek for device named `EL_XXXXXXXX`, where 8-letter alphanumeric string
   is lock serial number. Connection to lock does not require pairing and any kind of PIN.
3. Following Bluetooth GATT services and characteristics are available:
   - `00002a19-0000-1000-8000-00805f9b34fb` - battery level
   - `58af3dca-6fc0-4fa3-9464-74662f043a3b` - write commands
   - `58af3dca-6fc0-4fa3-9464-74662f043a3a` - notification channel
   
   More can be found after decompiling official app (try JADX)
4. To lock and unlock, notification channel should be listened to, and valid packet must be written to second UUID from the list above.
5. If lock wasn't used for a while or batteries were replaced, there will be notification sent beginning with `0x09` which means
    time synchronisation request. There are also notifications for beginning and end of lock/unlock procedure.
    
    Map of first bytes of notifications and corresponding consts can also be found in decompiled APK (search for something like `TX_SET_SYS_TIME_REQ`).
    
    If time sync was requested, new time sync packet need to be send and lock/unlock packet should be send again to do the action.
    
## Packet structure

Check **packet.py** to see how packet is generated.

### Lock and unlock

| Byte(s) | Description                                               |
|---------|-----------------------------------------------------------|
| 1       | Packet type: 0x01 - lock/unlock                           |
| 2       | ? - need to be `0x50`                                     |
| 3-6     | Unix timestamp                                            |
| 7       | Mode (0x00 - unlock and lock, 0x01 - unlock, 0x02 - lock) |
| 8-21    | 14 first bytes of HMAC                                    |

### Sync time

| Byte(s) | Description                                               |
|---------|-----------------------------------------------------------|
| 1       | Packet type: 0x01 - lock/unlock, 0x08 - set time          |
| 2       | ? - need to be `0x40`                                     |
| 3-6     | Unix timestamp                                            |
| 7-21    | 15 first bytes of HMAC                                    |

### HMAC calculation

You can use [this site](https://www.liavaag.org/English/SHA-Generator/HMAC/) to calculate HMAC.  
As input, take all previous fields of packet (and select HEX as input type).  
Key is your BT sign key, variant is SHA-1.
