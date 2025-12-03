# Security Guidelines

## ⚠️ Important Security Notice

This document outlines security best practices for the OneDevelopment Agent project.

## Environment Variables

### Never Commit Secrets

**NEVER** commit the following to version control:
- `.env` files containing actual credentials
- API keys (OpenAI, AWS, etc.)
- Database passwords
- Server IP addresses
- SSH keys or certificates
- ngrok URLs or temporary tunnel URLs

### Use `.env.example` Templates

- Commit `.env.example` files with placeholder values
- Use `<YOUR_VALUE>` or `placeholder` for sensitive values
- Document what each variable is for
- Keep actual `.env` files in `.gitignore`

### .gitignore Configuration

Ensure your `.gitignore` includes:
```
.env
.env.local
.env.production
.env.*.local
*.pem
*.key
secrets/
```

## Server Configuration

### IP Address Security

- **DO NOT** hardcode server IP addresses in source code
- **DO NOT** commit production server IPs to repositories
- Use environment variables for all server addresses
- Use placeholders like `<YOUR_SERVER_IP>` in documentation
- Consider using domain names instead of IP addresses

### SSH Security

- Use key-based authentication, not passwords
- Keep private keys (`*.pem`, `*.key`) out of version control
- Use `chmod 400` for private key files
- Rotate SSH keys regularly
- Use AWS Systems Manager Session Manager when possible

## API Keys & Credentials

### OpenAI API Keys

- Store in environment variables only
- Never hardcode in source code
- Monitor usage for unexpected spikes (possible leak)
- Rotate keys if compromised
- Use API key restrictions when available

### Database Credentials

- Use strong, unique passwords
- Store in environment variables or AWS Secrets Manager
- Use IAM authentication for AWS RDS when possible
- Regularly rotate credentials
- Never use default passwords

### AWS Credentials

- Use IAM roles instead of access keys when possible
- Never commit AWS credentials to version control
- Use least-privilege IAM policies
- Enable MFA for AWS accounts
- Rotate access keys every 90 days

## Production Deployment

### HTTPS/TLS

- Always use HTTPS in production
- Obtain SSL/TLS certificates (Let's Encrypt is free)
- Enable HSTS (HTTP Strict Transport Security)
- Redirect HTTP to HTTPS

### Django Security Settings

Production settings should include:
```python
DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY')  # Use strong, random key
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

### CORS Configuration

- Only allow trusted origins in CORS_ALLOWED_ORIGINS
- Never use `CORS_ALLOW_ALL_ORIGINS = True` in production
- Be specific with allowed methods and headers

## AWS Security Best Practices

### EC2 Instances

- Keep security groups restrictive
- Only open necessary ports (80, 443, 22)
- Restrict SSH access to known IP ranges
- Use Elastic IPs but don't commit them to repos
- Enable AWS GuardDuty for threat detection

### S3 Buckets

- Never make buckets public unless absolutely necessary
- Use bucket policies to restrict access
- Enable versioning for important data
- Use encryption at rest

### RDS Databases

- Use VPC for network isolation
- Enable encryption at rest
- Use SSL/TLS for connections
- Restrict security group access
- Enable automated backups

## Monitoring & Response

### Detect Leaks

- Monitor API usage for anomalies
- Set up billing alerts
- Use AWS CloudWatch for monitoring
- Enable AWS CloudTrail for audit logs

### If Credentials are Compromised

1. **Immediately** rotate the compromised credential
2. Review logs for unauthorized access
3. Assess what data may have been exposed
4. Update all instances using the old credential
5. Consider git history sanitization if committed
6. Notify affected parties if data was exposed

## Secret Scanning

Use tools to prevent accidental commits:
- `git-secrets` - Prevents committing secrets
- `gitleaks` - Scans git repos for secrets
- GitHub secret scanning (enabled by default)
- Pre-commit hooks for validation

## Code Review Checklist

Before committing, verify:
- [ ] No `.env` files with real values
- [ ] No API keys or passwords in code
- [ ] No hardcoded IP addresses or URLs
- [ ] All secrets use environment variables
- [ ] `.gitignore` is properly configured
- [ ] Documentation uses placeholders

## Incident Response

If you discover a security issue:
1. Do NOT discuss publicly
2. Email the maintainer directly
3. Include details about the issue
4. Allow time for patch before disclosure
5. Follow responsible disclosure practices

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)
- [12-Factor App Security](https://12factor.net/)

---

**Remember:** Security is everyone's responsibility. When in doubt, ask!

