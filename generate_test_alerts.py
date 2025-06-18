import os

# Use a path in the user's home directory
alert_dir = os.path.expanduser("~/snort_test")
alert_file = os.path.join(alert_dir, "alert")

# Sample Snort alert lines (unified2 or fast alert format)
sample_alerts = [
    "[**] [1:1000001:0] Test alert: Possible TCP scan [**]\n[Priority: 2] {TCP} 192.168.1.100:12345 -> 192.168.1.200:80\n",
    "[**] [1:1000002:0] Test alert: Suspicious ICMP traffic [**]\n[Priority: 3] {ICMP} 10.0.0.5 -> 10.0.0.1\n",
    "[**] [1:1000003:0] Test alert: Potential exploit attempt [**]\n[Priority: 1] {UDP} 172.16.0.10:53 -> 8.8.8.8:53\n"
]

os.makedirs(alert_dir, exist_ok=True)
with open(alert_file, "w") as f:
    f.writelines(sample_alerts)

print(f"Test alert data written to {alert_file}")