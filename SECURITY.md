# Snowflake AI Agent - Security Guide

This guide explains secure authentication methods for connecting to Snowflake without exposing passwords in configuration files.

## 🔐 Authentication Methods (Recommended Order)

### 1. Interactive Password Prompt (Best for Development)
**✅ Most Secure for Local Development**

Set in `.env` file:
```env
SNOWFLAKE_PASSWORD=PROMPT
```

The agent will securely prompt for your password when connecting:
```
Please enter password for Snowflake user 'your_username':
[password input is hidden]
```

**Pros:**
- Password never stored in files
- Works immediately
- No additional setup required

**Cons:**
- Not suitable for automated/production environments
- Must enter password each time

### 2. Private Key Authentication (Best for Production)
**✅ Most Secure Overall**

#### Setup Steps:

1. **Generate RSA key pair:**
   ```powershell
   # Generate private key
   openssl genrsa -out snowflake_key.pem 2048
   
   # Generate public key
   openssl rsa -in snowflake_key.pem -pubout -out snowflake_key.pub
   ```

2. **Add public key to Snowflake user:**
   ```sql
   ALTER USER your_username SET RSA_PUBLIC_KEY='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...';
   ```

3. **Configure `.env` file:**
   ```env
   SNOWFLAKE_PRIVATE_KEY_PATH=C:\path\to\snowflake_key.pem
   SNOWFLAKE_PRIVATE_KEY_PASSPHRASE=your_key_passphrase
   # Remove or comment out SNOWFLAKE_PASSWORD
   ```

**Pros:**
- No password needed
- Suitable for production
- Keys can be rotated
- More secure than passwords

**Cons:**
- Requires initial setup
- Need to manage key files securely

### 3. SSO/Browser Authentication (Best for Enterprise)
**✅ Best for SSO Environments**

Configure `.env` file:
```env
SNOWFLAKE_AUTHENTICATOR=externalbrowser
# Remove or comment out SNOWFLAKE_PASSWORD
```

When connecting, your default browser will open for SSO login.

**Pros:**
- Uses existing SSO credentials
- No password storage
- Integrates with enterprise authentication

**Cons:**
- Requires browser access
- Only works in SSO environments
- Not suitable for headless deployments

### 4. Environment Variable Password (Better than Hardcoded)
**⚠️ Better than hardcoded, but not ideal**

Set password in secure environment variable:
```powershell
# PowerShell
$env:SNOWFLAKE_PASSWORD_SECURE = "your_actual_password"

# Command Prompt
set SNOWFLAKE_PASSWORD_SECURE=your_actual_password
```

Configure `.env` file:
```env
# Leave SNOWFLAKE_PASSWORD empty or remove it
# SNOWFLAKE_PASSWORD=
```

**Pros:**
- Password not in files
- Works for automation
- No additional setup

**Cons:**
- Password still in memory/environment
- Can be visible in process lists
- Not as secure as key-based auth

### 5. OAuth Token Authentication (For API Integration)
**✅ Good for API Integration**

Configure `.env` file:
```env
SNOWFLAKE_AUTHENTICATOR=oauth
SNOWFLAKE_OAUTH_TOKEN=your_oauth_token
```

**Pros:**
- Token-based security
- Can be scoped and revoked
- Good for API integrations

**Cons:**
- Requires OAuth setup
- Tokens need refresh handling
- Complex initial configuration

## 🛡️ Security Best Practices

### File Security
- **Never commit `.env` files** to version control
- Set restrictive file permissions on key files:
  ```powershell
  icacls snowflake_key.pem /inheritance:r /grant:r "%username%:F"
  ```
- Store keys in secure directories outside the project folder

### Environment Security
- Use different authentication methods for different environments:
  - **Development**: Interactive prompts
  - **Testing**: Private keys or environment variables
  - **Production**: Private keys or SSO
- Rotate credentials regularly
- Use separate Snowflake accounts/users for different environments

### Application Security
- The AI agent automatically:
  - Validates SQL queries for dangerous operations
  - Logs connection attempts (but not credentials)
  - Masks sensitive data in logs
  - Times out connections appropriately

### Network Security
- Use Snowflake's network policies to restrict access
- Consider VPN or private network connections
- Enable IP allowlisting where possible

## 🔧 Troubleshooting

### Common Issues

**"Private key authentication failed"**
- Verify key file path and permissions
- Check key format (should be PEM format)
- Ensure public key is correctly added to Snowflake user

**"SSO authentication failed"**
- Check if browser can access Snowflake SSO URL
- Verify SSO is configured for your user
- Try different browser if needed

**"Password prompt not working"**
- Ensure terminal supports secure input
- Try running from different terminal (PowerShell, Command Prompt)
- Check if running in IDE terminal vs system terminal

### Testing Authentication
```powershell
# Test connection with current configuration
python -m src.main test

# Test with verbose logging
$env:LOG_LEVEL = "DEBUG"
python -m src.main test
```

## 📝 Migration Guide

### From Password to Private Key Authentication

1. **Generate keys** (see Method 2 above)
2. **Update Snowflake user** with public key
3. **Update `.env` file**:
   ```env
   # Before
   SNOWFLAKE_PASSWORD=your_password
   
   # After
   SNOWFLAKE_PRIVATE_KEY_PATH=C:\secure\snowflake_key.pem
   # SNOWFLAKE_PASSWORD=  # Comment out or remove
   ```
4. **Test connection**
5. **Remove old password** from any remaining locations

### From Hardcoded to Prompt Authentication

Simply change `.env` file:
```env
# Before
SNOWFLAKE_PASSWORD=hardcoded_password

# After
SNOWFLAKE_PASSWORD=PROMPT
```

## 🚨 Security Incident Response

If credentials are compromised:

1. **Immediately change/rotate** affected credentials
2. **Check Snowflake access logs** for unauthorized usage
3. **Update authentication method** to more secure option
4. **Review and update** security practices
5. **Consider enabling** additional monitoring/alerting

## 📞 Support

For security questions or issues:
- Check Snowflake documentation on authentication
- Review application logs with DEBUG level
- Create issue in project repository (don't include credentials!)

Remember: **Security is a shared responsibility**. While this AI agent provides secure authentication options, you must implement and maintain proper security practices in your environment.