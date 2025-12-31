#!/bin/bash
# Development Environment Startup Script for Linux/macOS
# Start both frontend and backend services for sequence video generation

set -e

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting development environment...${NC}"
echo -e "${MAGENTA}Feature: Sequence Video Generation (2-6 images)${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}Warning: .env file not found!${NC}"
    echo -e "${YELLOW}Please copy .env.example to .env and configure DASHSCOPE_API_KEY${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

# Check if ffmpeg is installed (required for sequence video)
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}Warning: ffmpeg not found!${NC}"
    echo -e "${YELLOW}Sequence video generation requires ffmpeg.${NC}"
    echo -e "${YELLOW}Install it using:${NC}"
    echo -e "  ${CYAN}Ubuntu/Debian: sudo apt-get install ffmpeg${NC}"
    echo -e "  ${CYAN}macOS: brew install ffmpeg${NC}"
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend service
echo -e "\n${CYAN}Starting backend service (http://localhost:8000)...${NC}"
source venv/bin/activate
python main.py &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${GRAY}Waiting for backend to initialize...${NC}"
sleep 3

# Start frontend service
echo -e "${CYAN}Starting frontend service (http://127.0.0.1:3000)...${NC}"
cd web
npm run dev &
FRONTEND_PID=$!
cd ..

echo -e "\n${GREEN}Development environment started!${NC}"
echo -e "${YELLOW}- Frontend: http://127.0.0.1:3000${NC}"
echo -e "${YELLOW}- Backend:  http://localhost:8000${NC}"
echo -e "${YELLOW}- API Docs: http://localhost:8000/docs${NC}"
echo -e "\n${CYAN}Tip: Upload 2-6 images to generate sequence video${NC}"
echo -e "${GRAY}Press Ctrl+C to stop all services${NC}\n"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
