# SnortAI Frontend

A React-based frontend for SnortAI that provides a modern, responsive interface for analyzing Snort alerts.

## Features

- Real-time alert monitoring
- Interactive charts and visualizations
- Alert filtering and search
- Responsive design for all devices
- Snort branding and theme

## Prerequisites

- Node.js 16.x or later
- npm 7.x or later
- AWS CLI configured with appropriate S3 permissions

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file in the frontend directory:
```
REACT_APP_API_URL=http://localhost:8000
```

3. Start the development server:
```bash
npm start
```

The application will be available at http://localhost:3000

## Building for Production

To create a production build:

```bash
npm run build
```

This will create an optimized build in the `build/` directory.

## Deploying to S3

1. Create an S3 bucket for hosting:
```bash
aws s3 mb s3://snortai-frontend
```

2. Configure the bucket for static website hosting:
```bash
aws s3 website s3://snortai-frontend --index-document index.html --error-document index.html
```

3. Add a bucket policy to allow public access:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::snortai-frontend/*"
        }
    ]
}
```

4. Deploy the frontend:
```bash
npm run deploy
```

The application will be available at the S3 website endpoint.

## Development

- `npm start` - Start development server
- `npm test` - Run tests
- `npm run build` - Create production build
- `npm run deploy` - Deploy to S3

## Project Structure

```
frontend/
├── public/              # Static files
├── src/
│   ├── components/      # React components
│   ├── theme.ts         # Material-UI theme
│   ├── App.tsx          # Main application component
│   └── index.tsx        # Application entry point
└── package.json         # Dependencies and scripts
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
