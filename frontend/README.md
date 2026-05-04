# RAG System Frontend

Next.js-based frontend for the RAG (Retrieval-Augmented Generation) System.

## Features

- 💬 Modern chat interface similar to NotebookLM
- 📱 Responsive design
- 🔄 Real-time message streaming
- 📚 Chat history management
- 🎨 Clean and intuitive UI
- ⚡ Fast performance with Next.js
- 🎯 TypeScript for type safety

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

```bash
npm install
# or
yarn install
```

### Configuration

```bash
cp .env.example .env.local
# Edit .env.local with your settings
```

### Development

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
src/
├── pages/              # Next.js pages
├── components/         # React components
├── services/           # API client and services
├── hooks/              # Custom React hooks
├── types/              # TypeScript types
├── styles/             # Global styles
└── utils/              # Utility functions
```

## Key Components

### ChatWindow
Main chat interface component.

### MessageList
Displays messages in the conversation.

### InputArea
User input field and send button.

## Environment Variables

See `.env.example` for all available configuration options.

## API Integration

The frontend communicates with the FastAPI backend at `NEXT_PUBLIC_API_URL`.

### Main Endpoints

- `POST /api/v1/chat/message` - Send message
- `WebSocket /ws/chat/{session_id}` - Real-time chat
- `GET /api/v1/chat/history/{session_id}` - Get history

## Development Tips

- Use `npm run format` to format code
- Use `npm run lint` to check code style
- Use `npm run type-check` for TypeScript validation

## License

MIT
