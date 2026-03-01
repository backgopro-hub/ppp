# Bot Service Restart Instructions

## Why Restart is Needed

The telegram.py file has been updated with logging and validation for the key_name parameter. However, the bot service (bot.service) is still running the old code. To apply these changes, you need to restart the bot service.

## Manual Restart Instructions

Since you cannot use the command line, follow these steps to restart the bot service manually:

### Option 1: Using Your Hosting Control Panel

1. **Log in to your hosting control panel** (e.g., cPanel, Plesk, or your VPS provider's dashboard)

2. **Navigate to the Services or Process Manager section**
   - Look for "Services", "Process Manager", or "System Services"
   - Find the service named "bot" or "bot.service"

3. **Restart the service**
   - Click the "Restart" button next to the bot service
   - Wait for the service to fully restart (usually 5-10 seconds)

4. **Verify the restart succeeded** (see Verification Steps below)

### Option 2: Using SSH (If Available)

If you have SSH access but prefer not to use command line directly, you can use a web-based SSH terminal:

1. **Access your web-based SSH terminal** (many hosting providers offer this in their control panel)

2. **Run the restart command:**
   ```bash
   sudo systemctl restart bot.service
   ```

3. **Check the service status:**
   ```bash
   sudo systemctl status bot.service
   ```
   - You should see "active (running)" in green

### Option 3: Reboot the Server

If the above options are not available, you can reboot the entire server:

1. **Log in to your hosting control panel**

2. **Navigate to the Server or System section**

3. **Click "Reboot" or "Restart Server"**
   - This will restart all services, including the bot service
   - Wait 2-3 minutes for the server to fully restart

4. **Verify the bot service is running** (see Verification Steps below)

## Verification Steps

After restarting the bot service, verify that the new code is running:

### 1. Check Bot Service Logs

Look for the new logging messages in your bot service logs:

- `[Elusion Web] profile_menu_hook: extracted key_name='...' from target_key`
- `[Elusion Web] _create_connect_buttons: creating URL with key_name='...'`
- `[Elusion Web] _create_connect_buttons: frontend_url_with_key='...'`

If you see these messages, the new code is running!

### 2. Test the WebApp

1. Open your Telegram bot
2. Click the profile button
3. Click the "📲 Подключить VPN" button
4. The WebApp should load without the "Нет данных" error
5. Check the browser console (F12) - there should be NO "No key_name available" error

### 3. Check Service Status

If you have access to service status information:

- The bot service should show as "active (running)"
- The service restart timestamp should be recent (within the last few minutes)

## Troubleshooting

### Problem: Service won't restart

**Solution:**
- Check if there are any syntax errors in telegram.py
- Review the bot service error logs for details
- Try rebooting the entire server instead

### Problem: Still seeing "No key_name available" error

**Possible causes:**
1. **Service didn't restart properly**
   - Verify the service is running
   - Check the service restart timestamp
   - Try restarting again

2. **Old code is cached**
   - Clear your browser cache
   - Try opening the WebApp in an incognito/private window
   - Wait 1-2 minutes and try again

3. **key_name is empty**
   - Check the bot service logs for validation warnings
   - Look for: `[Elusion Web] profile_menu_hook: key_name is empty, cannot create buttons`
   - This means the subscription key doesn't have an email address set

### Problem: Can't find bot service in control panel

**Solution:**
- Contact your hosting provider support
- Ask them to restart the "bot.service" or "telegram bot service"
- Provide them with this document for reference

## Expected Results After Restart

Once the bot service is successfully restarted with the new code:

✅ Bot service logs will show key_name extraction and URL creation messages
✅ WebApp will load subscription data correctly
✅ No "Нет данных" error in the WebApp
✅ No "No key_name available" error in browser console
✅ Profile button will work correctly for users with multiple subscriptions

## Need Help?

If you continue to experience issues after following these instructions:

1. Check the bot service logs for error messages
2. Verify the telegram.py file contains the new logging code
3. Ensure the bot service has read permissions for telegram.py
4. Contact your hosting provider for assistance with service management

---

**Note:** These changes only add logging and validation - they do not modify the core button creation logic. All existing functionality should continue to work as before.
