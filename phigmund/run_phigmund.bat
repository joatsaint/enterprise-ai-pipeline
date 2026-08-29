@echo off
title Phigmund Email Response Generator
cd /d "%~dp0.."
echo.
echo  =====================================================
echo   PHIGMUND EMAIL RESPONSE GENERATOR
echo   Powered by 25 years of accumulated patience
echo  =====================================================
echo.
echo  Starting Phigmund...
echo  (If this fails with "credit balance too low",
echo   top up at console.anthropic.com first)
echo.
python phigmund/email_responder.py --save
echo.
pause
