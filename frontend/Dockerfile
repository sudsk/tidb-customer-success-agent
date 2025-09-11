# Bulletproof Dockerfile that forces clean installs
FROM node:18-alpine AS build

WORKDIR /app

# Clear npm cache and set registry
RUN npm cache clean --force
RUN npm config set registry https://registry.npmjs.org/

# Copy package.json only
COPY package.json ./

# Remove any existing lock files and node_modules from COPY
RUN rm -rf node_modules package-lock.json

# Install with specific flags to avoid corruption
RUN npm install --no-package-lock --legacy-peer-deps --verbose

# Verify react-scripts is properly installed
RUN ls -la node_modules/.bin/react-scripts
RUN ls -la node_modules/react-scripts/

# Copy source code AFTER successful install
COPY . .

# Build with explicit path
RUN ./node_modules/.bin/react-scripts build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
