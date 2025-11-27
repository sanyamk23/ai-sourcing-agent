# Production Deployment Checklist

Use this checklist before deploying to production.

## Pre-Deployment

### Configuration
- [ ] `.env` file created with production values
- [ ] `SECRET_KEY` changed to random value
- [ ] `GROQ_API_KEY` configured
- [ ] `LINKEDIN_USERNAME` and `LINKEDIN_PASSWORD` set
- [ ] `ALLOWED_ORIGINS` restricted to your domain
- [ ] `API_WORKERS` set appropriately (number of CPU cores)
- [ ] `LOG_LEVEL` set to `INFO` or `WARNING`
- [ ] `DATABASE_URL` configured (consider PostgreSQL for production)

### Security
- [ ] All secrets in environment variables (not in code)
- [ ] `.env` file in `.gitignore`
- [ ] CORS origins restricted
- [ ] Rate limiting configured
- [ ] HTTPS enabled (via reverse proxy)
- [ ] Firewall rules configured
- [ ] Strong passwords used
- [ ] API keys rotated regularly

### Infrastructure
- [ ] Server/instance provisioned
- [ ] Sufficient resources (CPU, RAM, disk)
- [ ] Chrome/Chromium installed
- [ ] Docker installed (if using Docker)
- [ ] Reverse proxy configured (nginx/Apache)
- [ ] SSL certificate installed
- [ ] Domain DNS configured
- [ ] Backup strategy in place

### Testing
- [ ] All tests passing (`make test`)
- [ ] Health check working (`/health` endpoint)
- [ ] API endpoints tested
- [ ] LinkedIn scraping tested
- [ ] End-to-end pipeline tested
- [ ] Load testing performed
- [ ] Error handling verified

### Monitoring
- [ ] Logging configured
- [ ] Log rotation enabled
- [ ] Health check monitoring set up
- [ ] Error alerting configured
- [ ] Metrics collection enabled
- [ ] Uptime monitoring active

### Documentation
- [ ] README.md updated
- [ ] API documentation current
- [ ] Deployment guide reviewed
- [ ] Environment variables documented
- [ ] Troubleshooting guide available

## Deployment

### Docker Deployment
- [ ] Docker image built (`make docker-build`)
- [ ] Image tested locally
- [ ] Environment variables configured
- [ ] Volumes mounted correctly
- [ ] Ports exposed properly
- [ ] Container started (`make docker-run`)
- [ ] Health check passing
- [ ] Logs reviewed

### Direct Deployment
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] System dependencies installed (Chrome)
- [ ] Environment configured
- [ ] Service/systemd configured
- [ ] Application started
- [ ] Health check passing
- [ ] Logs reviewed

## Post-Deployment

### Verification
- [ ] API accessible from internet
- [ ] Health endpoint responding
- [ ] Test job submitted successfully
- [ ] Candidates returned correctly
- [ ] LinkedIn scraping working
- [ ] Database persisting data
- [ ] Logs being written

### Performance
- [ ] Response times acceptable
- [ ] Memory usage normal
- [ ] CPU usage reasonable
- [ ] No memory leaks
- [ ] Scraping completing in reasonable time

### Monitoring Setup
- [ ] Uptime monitoring configured
- [ ] Error tracking active
- [ ] Log aggregation working
- [ ] Alerts configured
- [ ] Dashboard created (optional)

### Backup
- [ ] Database backup scheduled
- [ ] Backup restoration tested
- [ ] Backup retention policy set
- [ ] Off-site backup configured

## Ongoing Maintenance

### Daily
- [ ] Check health endpoint
- [ ] Review error logs
- [ ] Monitor resource usage

### Weekly
- [ ] Review application logs
- [ ] Check for errors/warnings
- [ ] Verify backups
- [ ] Review performance metrics

### Monthly
- [ ] Update dependencies
- [ ] Rotate API keys
- [ ] Review security
- [ ] Test backup restoration
- [ ] Review and optimize

### Quarterly
- [ ] Security audit
- [ ] Performance review
- [ ] Capacity planning
- [ ] Documentation update

## Rollback Plan

If issues occur:

1. **Immediate Actions**
   - [ ] Stop the application
   - [ ] Check logs for errors
   - [ ] Verify configuration

2. **Rollback Steps**
   - [ ] Revert to previous version
   - [ ] Restore database backup (if needed)
   - [ ] Restart application
   - [ ] Verify functionality

3. **Post-Rollback**
   - [ ] Document the issue
   - [ ] Identify root cause
   - [ ] Fix in development
   - [ ] Test thoroughly
   - [ ] Redeploy when ready

## Emergency Contacts

- **System Admin**: [contact info]
- **Developer**: [contact info]
- **On-Call**: [contact info]

## Useful Commands

```bash
# Check health
curl https://your-domain.com/health

# View logs
docker-compose logs -f
# or
tail -f logs/app.log

# Restart service
docker-compose restart
# or
systemctl restart ai-candidate-sourcing

# Check resource usage
docker stats
# or
htop

# Database backup
cp data/candidates.db backups/candidates_$(date +%Y%m%d).db

# Check disk space
df -h
```

## Notes

- Keep this checklist updated
- Document any deviations
- Share with team members
- Review after each deployment

---

**Last Updated**: 2024-11-27
**Reviewed By**: [Your Name]
**Next Review**: [Date]
