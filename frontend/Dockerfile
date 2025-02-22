FROM node:20.17.0-slim

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Expose port 3000
EXPOSE 3000

# Set the environment variable
ENV WATCHPACK_POLLING=true

# Build the application
RUN npm run build

# Start the application
CMD ["npm", "start"]
