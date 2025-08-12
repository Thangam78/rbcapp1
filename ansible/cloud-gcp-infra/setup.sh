#!/bin/bash

# This script runs on the first boot of a new VM to configure the data disk

# Variables (will be passed as metadata or derived)
DISK_NAME="<VM_NAME>-data-disk" # Name of the disk created by gcloud

# Check if the disk exists and is not already formatted
if ! lsblk | grep -q "/dev/disk/by-id/google-$DISK_NAME-part1"; then
  echo "Disk /dev/disk/by-id/google-$DISK_NAME found. Partitioning and formatting..."
  # Partition the disk
  parted -s /dev/disk/by-id/google-$DISK_NAME mklabel gpt mkpart primary ext4 0% 100%

  # Format the partition
  mkfs.ext4 -F /dev/disk/by-id/google-$DISK_NAME-part1

  # Create mount point
  mkdir -p /mnt/data

  # Add to /etc/fstab for persistent mounting
  echo "/dev/disk/by-id/google-$DISK_NAME-part1 /mnt/data ext4 defaults,nofail 0 2" | tee -a /etc/fstab

  # Mount the disk
  mount /mnt/data
  echo "Disk /dev/disk/by-id/google-$DISK_NAME configured and mounted at /mnt/data."
else
  echo "Disk /dev/disk/by-id/google-$DISK_NAME already partitioned or mounted. Skipping."
fi

# Ensure SSH service is running (good practice, especially after potential issues)
systemctl enable sshd
systemctl start sshd

# Install Python (for Ansible)
sudo apt update
sudo apt install -y python3 python3-pip

