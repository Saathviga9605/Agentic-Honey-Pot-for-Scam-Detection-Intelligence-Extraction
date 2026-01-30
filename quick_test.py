from detector import detect_scam

print('Testing key scenarios...\n')

tests = [
    ('Share your UPI ID to avoid account suspension', True),
    ('Your statement is ready', False),
    ('Send OTP now', True),
    ('Thanks for banking with us', False),
]

for text, expected in tests:
    result = detect_scam({'text': text})
    status = '[OK]' if result['scamDetected'] == expected else '[FAIL]'
    print(f'{status} "{text}"')
    print(f'     Detected: {result["scamDetected"]}, Confidence: {result["confidence"]:.2f}\n')

print('\n=== ALL KEY SCENARIOS TESTED ===')
