# NAS Gateway

A simple Docker-based gateway that automatically wakes up your NAS via Wake-on-LAN (WOL) when accessed. It displays a loading screen while the NAS is booting and automatically redirects you to the NAS interface once it comes online. The stack also includes a Homebridge container.

## Setup

1. Copy the `.env.template` file to `.env`:
   ```sh
   cp .env.template .env
   ```
2. Update the `.env` file with your NAS details:
   - `NAS_IP`: The IP address of your NAS.
   - `NAS_MAC`: The MAC address of your NAS (required for Wake-on-LAN).
   - `CHECK_PORT`: The port to check if the NAS is online (default `80`).
   - `REDIRECT_URL`: The URL to redirect to once the NAS is online.

3. Start the services using Docker Compose:
   ```sh
   docker compose up -d
   ```

## Components
- **nas-gateway**: A Flask web application that handles the WOL logic, connection polling, and redirection.
- **homebridge**: Runs alongside the gateway to manage smart home devices.
