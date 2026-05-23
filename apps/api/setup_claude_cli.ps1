# Claude CLI Setup Script for Windows
# Run this in PowerShell as Administrator

Write-Host "=" -NoNewline; Write-Host ("=" * 69)
Write-Host "🚀 Claude CLI Setup for Mavericks Ascend"
Write-Host "=" -NoNewline; Write-Host ("=" * 69)
Write-Host ""

# Step 1: Check if Claude CLI is already installed
Write-Host "Step 1: Checking if Claude CLI is installed..."
Write-Host "-" -NoNewline; Write-Host ("-" * 69)

try {
    $version = claude --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Claude CLI is already installed: $version"
        $skipInstall = $true
    } else {
        $skipInstall = $false
    }
} catch {
    $skipInstall = $false
}

if (-not $skipInstall) {
    Write-Host "📦 Claude CLI not found. Installing..."
    Write-Host ""
    
    # Step 2: Install Claude CLI
    Write-Host "Step 2: Installing Claude CLI..."
    Write-Host "-" -NoNewline; Write-Host ("-" * 69)
    Write-Host ""
    Write-Host "Running: irm https://claude.ai/install.ps1 | iex"
    Write-Host ""
    
    try {
        irm https://claude.ai/install.ps1 | iex
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Claude CLI installed successfully!"
        } else {
            Write-Host ""
            Write-Host "❌ Installation failed. Please try manually:"
            Write-Host "   irm https://claude.ai/install.ps1 | iex"
            exit 1
        }
    } catch {
        Write-Host ""
        Write-Host "❌ Installation error: $_"
        Write-Host ""
        Write-Host "Please install manually:"
        Write-Host "   irm https://claude.ai/install.ps1 | iex"
        exit 1
    }
} else {
    Write-Host "⏭️  Skipping installation (already installed)"
}

Write-Host ""

# Step 3: Verify installation
Write-Host "Step 3: Verifying installation..."
Write-Host "-" -NoNewline; Write-Host ("-" * 69)

try {
    $version = claude --version
    Write-Host "✅ Verified: $version"
} catch {
    Write-Host "❌ Verification failed. Please reinstall."
    exit 1
}

Write-Host ""

# Step 4: Authenticate
Write-Host "Step 4: Authentication"
Write-Host "-" -NoNewline; Write-Host ("-" * 69)
Write-Host ""
Write-Host "You need to authenticate Claude CLI with your Claude account."
Write-Host ""
Write-Host "Choose an option:"
Write-Host "  1. Interactive Login (opens browser)"
Write-Host "  2. Generate Token (for automation)"
Write-Host "  3. Skip (already authenticated)"
Write-Host ""

$choice = Read-Host "Enter choice (1/2/3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🔐 Starting interactive login..."
        Write-Host "   This will open your browser"
        Write-Host ""
        claude auth login
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Authentication successful!"
        } else {
            Write-Host ""
            Write-Host "❌ Authentication failed"
            Write-Host "   You can try again later with: claude auth login"
        }
    }
    "2" {
        Write-Host ""
        Write-Host "🔑 Generating long-lived token..."
        Write-Host ""
        Write-Host "⚠️  IMPORTANT: Copy this token and add it to your .env file"
        Write-Host "   as CLAUDE_CODE_OAUTH_TOKEN=your-token-here"
        Write-Host ""
        claude setup-token
        Write-Host ""
        Write-Host "📝 Save this token in apps/api/.env:"
        Write-Host "   CLAUDE_CODE_OAUTH_TOKEN=the-token-shown-above"
    }
    "3" {
        Write-Host ""
        Write-Host "⏭️  Skipping authentication"
        Write-Host "   If you need to authenticate later, run: claude auth login"
    }
    default {
        Write-Host ""
        Write-Host "Invalid choice. Run 'claude auth login' manually when ready."
    }
}

Write-Host ""

# Step 5: Test Claude CLI
Write-Host "Step 5: Testing Claude CLI..."
Write-Host "-" -NoNewline; Write-Host ("-" * 69)
Write-Host ""
Write-Host "Running test command: claude -p 'Say hello'"
Write-Host ""

try {
    $response = claude -p "Say 'Hello!' in one word" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Test successful!"
        Write-Host "   Response: $response"
    } else {
        Write-Host "⚠️  Test failed: $response"
        Write-Host ""
        Write-Host "If you see authentication errors, run:"
        Write-Host "   claude auth login"
    }
} catch {
    Write-Host "⚠️  Test error: $_"
}

Write-Host ""
Write-Host "=" -NoNewline; Write-Host ("=" * 69)
Write-Host "✅ Setup Complete!"
Write-Host "=" -NoNewline; Write-Host ("=" * 69)
Write-Host ""

Write-Host "📝 Next Steps:"
Write-Host ""
Write-Host "1. Test the setup:"
Write-Host "   python test_claude_cli_setup.py"
Write-Host ""
Write-Host "2. Start your API server:"
Write-Host "   uvicorn app.main:app --reload"
Write-Host ""
Write-Host "3. Test AI endpoints:"
Write-Host "   http://localhost:8000/api/v1/ai/status"
Write-Host ""
Write-Host "4. For production (when ready):"
Write-Host "   - Get Anthropic API key"
Write-Host "   - Change AI_PROVIDER=anthropic in .env"
Write-Host ""
Write-Host "🎉 You're ready to develop with AI features!"
Write-Host ""
