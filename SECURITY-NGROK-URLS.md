# 🔒 Security Notice: ngrok URLs

## ⚠️ CRITICAL SECURITY ISSUE

**A hardcoded public ngrok tunnel URL was found in this repository's version control history.**

### What Happened

The ngrok URL `https://5d812f2e82fa.ngrok-free.app` was committed to version control in multiple files:
- PowerShell scripts (`SET_AVATAR_URL.ps1`, `RESTART_SERVERS.ps1`, `RESTART_SERVERS_V2.ps1`)
- Documentation files (`DEPLOY_AVATAR_TO_AWS.md`, `TEST_AVATAR_FROM_UI.md`, etc.)

### Why This Is a Problem

1. **Public Access**: ngrok URLs are publicly accessible on the internet
2. **Git History**: Even after removal, URLs remain in git history forever
3. **Attack Vector**: Anyone with the URL can potentially access your local avatar service
4. **No Authentication**: The exposed service may not have proper authentication

### Immediate Actions Taken

✅ **All hardcoded URLs have been replaced with placeholders**
✅ **Scripts now prompt for URLs or use environment variables**
✅ **Documentation updated with security warnings**
✅ **This security notice created**

### Required Actions

#### 1. Invalidate the Exposed URL

The exposed ngrok tunnel should be considered compromised:

```powershell
# Stop the current ngrok tunnel
# Find ngrok process
Get-Process | Where-Object {$_.ProcessName -like "*ngrok*"} | Stop-Process -Force

# Start a NEW tunnel (this will generate a new URL)
ngrok http 8000
```

**Note:** The old URL (`https://5d812f2e82fa.ngrok-free.app`) will no longer work once you restart ngrok.

#### 2. Update Environment Variables

Set the new ngrok URL using the provided script:

```powershell
.\SET_AVATAR_URL.ps1
```

This will prompt you for your new ngrok URL and set it securely.

#### 3. Update AWS Backend

If you've configured AWS to use the old URL:

```bash
ssh your-aws-server

# Update with your NEW ngrok URL
export AVATAR_SERVICE_URL=https://YOUR_NEW_NGROK_URL.ngrok-free.app

# Restart backend
sudo systemctl restart your-backend-service
```

#### 4. Review Access Logs (Optional but Recommended)

Check if there were any unauthorized access attempts:

```powershell
# Check ngrok web interface
# Visit: http://localhost:4040
# Review request logs for suspicious activity
```

### Best Practices Going Forward

#### ✅ DO:

1. **Use Environment Variables**: Always store ngrok URLs in environment variables
   ```powershell
   $env:AVATAR_SERVICE_URL = "https://your-url.ngrok-free.app"
   ```

2. **Use .env Files**: Store secrets in `.env` files (already in `.gitignore`)
   ```bash
   # .env
   AVATAR_SERVICE_URL=https://your-url.ngrok-free.app
   ```

3. **Use Configuration Scripts**: Use `SET_AVATAR_URL.ps1` which prompts for URLs

4. **Rotate URLs Regularly**: Restart ngrok periodically to get new URLs

5. **Use ngrok Authentication**: Add basic auth to your ngrok tunnel
   ```powershell
   ngrok http 8000 --basic-auth="username:password"
   ```

6. **Consider Reserved Domains**: Use ngrok paid plan for reserved domains with better control

#### ❌ DON'T:

1. **Never Hardcode URLs**: Don't put ngrok URLs directly in scripts or code
2. **Never Commit Secrets**: Don't commit `.env` files or URLs to git
3. **Don't Share URLs Publicly**: Treat ngrok URLs like passwords
4. **Don't Use Same URL Long-term**: Rotate URLs regularly
5. **Don't Skip Authentication**: Always use authentication for production

### Technical Details

#### What is ngrok?

ngrok creates a public tunnel to your local machine:
- Exposes `localhost:8000` to the internet
- Provides a public HTTPS URL
- Anyone with the URL can access your service
- URLs change each time ngrok restarts (free tier)

#### Why We Use ngrok

In this project, ngrok allows:
- AWS frontend to connect to local avatar service
- GPU processing on local machine (saves cloud GPU costs)
- Development and testing without cloud deployment

#### Security Layers

1. **URL Secrecy**: Keep ngrok URLs private (primary defense)
2. **Firewall**: Windows Firewall protects other ports
3. **Application Auth**: Avatar service should implement authentication
4. **Network Isolation**: Only expose necessary services

### Additional Security Measures

#### 1. Add Authentication to Avatar Service

Update `avatar_service/avatar_server_final.py`:

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import os

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.getenv("AVATAR_USERNAME", "admin")
    correct_password = os.getenv("AVATAR_PASSWORD", "changeme")
    
    is_correct_username = secrets.compare_digest(
        credentials.username.encode("utf8"), correct_username.encode("utf8")
    )
    is_correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"), correct_password.encode("utf8")
    )
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.post("/generate")
async def generate(request: GenerateRequest, username: str = Depends(verify_credentials)):
    # Your existing code
    pass
```

#### 2. Use ngrok IP Restrictions (Paid Feature)

```powershell
# Restrict access to specific IPs (your AWS server)
ngrok http 8000 --cidr-allow="YOUR_AWS_IP/32"
```

#### 3. Monitor Access

```powershell
# Check ngrok dashboard
Start-Process "http://localhost:4040"

# Review requests in real-time
# Look for unexpected sources or patterns
```

#### 4. Use VPN or Private Tunnel (Alternative)

Consider alternatives to public ngrok:
- **Tailscale**: Private mesh VPN
- **WireGuard**: Secure VPN tunnel
- **ngrok Reserved Domains**: Better control and monitoring
- **Cloudflare Tunnel**: Free alternative with better security

### Monitoring and Alerts

#### Set Up Monitoring

1. **ngrok Dashboard**: http://localhost:4040
2. **Application Logs**: Check avatar service logs
3. **Windows Firewall Logs**: Monitor connection attempts

#### Signs of Compromise

Watch for:
- Unexpected requests in ngrok dashboard
- High bandwidth usage
- Requests from unknown IPs
- Failed authentication attempts
- Service slowdowns or crashes

### Recovery Checklist

If you suspect unauthorized access:

- [ ] Stop ngrok immediately
- [ ] Review access logs
- [ ] Check for unauthorized files or changes
- [ ] Scan system for malware
- [ ] Start new ngrok tunnel with new URL
- [ ] Add authentication to avatar service
- [ ] Update all configuration with new URL
- [ ] Monitor for suspicious activity

### Questions and Answers

**Q: Is my system compromised?**
A: Unlikely. The exposed service is limited to avatar generation. However, restart ngrok to be safe.

**Q: Can attackers access my files?**
A: No. ngrok only exposes the specific port (8000) and the avatar service running on it.

**Q: Do I need to change passwords?**
A: No system passwords are exposed. However, add authentication to the avatar service.

**Q: Should I stop using ngrok?**
A: No, but use it securely. Follow the best practices in this document.

**Q: Can I remove the URL from git history?**
A: Yes, but it's complex and requires force-pushing. Since the URL is invalidated by restarting ngrok, this is optional.

### Resources

- [ngrok Security Best Practices](https://ngrok.com/docs/secure-tunnels/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Security Guidelines](https://owasp.org/)

### Summary

✅ **Issue Identified**: Hardcoded ngrok URL in version control
✅ **Risk Level**: Medium (limited exposure, easily mitigated)
✅ **Immediate Fix**: Restart ngrok to invalidate old URL
✅ **Long-term Fix**: Use environment variables and authentication
✅ **Prevention**: Follow security best practices outlined above

---

**Last Updated**: December 3, 2025
**Status**: Resolved - All hardcoded URLs removed
**Action Required**: Restart ngrok and update configuration

For questions or concerns, review this document and the updated scripts.

