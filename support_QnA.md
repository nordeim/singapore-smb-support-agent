📋 Implementation Plan: Phase 9 - Data Preparation & Ingestion
---
Context
- Phase 8 (Frontend): ✅ Complete - 1,400+ lines of React/TypeScript code
- Phase 3 (Ingestion Pipeline): ✅ Complete - Includes CLI tool (ingest_documents.py)
- Backend APIs: ✅ Complete - Ready to receive messages
Phase 9 Goal: Prepare sample documents and test ingestion pipeline.
---
Architecture Overview
Phase 9: Data Preparation & Ingestion
├── 9.1 Create Sample Documents
│   ├── FAQs (pricing, hours, services, returns, shipping)
│   ├── Products Catalog (names, descriptions, pricing, availability)
│   └── Policies (terms, privacy, returns, shipping)
├── 9.2 Organize Data Directory
│   └── backend/data/ structure
├── 9.3 Test Ingestion Pipeline
│   ├── Test CLI tool with sample docs
│   ├── Verify Qdrant collection population
│   └── Test RAG retrieval
└── 9.4 Document & Verify
    └── Create documentation of ingested data
---
Singapore SMB Business Context
Business Type: E-commerce / Service Provider
Operating Hours: 9:00 AM - 6:00 PM (Monday-Friday, SGT)
Location: Singapore
Timezone: Asia/Singapore (GMT+8)
Business Model: B2B/B2C with customer support needs
---
Data Strategy
| Document Type | Count | Format | Content |
|--------------|-------|--------|---------|
| FAQs | 20+ | Markdown | Pricing, hours, services, returns, shipping |
| Products | 10+ | Markdown | Product details, pricing, availability |
| Policies | 4 | Markdown | Terms, privacy, returns, shipping |
---
Implementation Order
1. 9.1 Create backend/data/ directory structure
2. 9.2 Create FAQ documents (20 files)
3. 9.3 Create Product documents (10 files)
4. 9.4 Create Policy documents (4 files)
5. 9.5 Test ingestion with CLI tool
6. 9.6 Verify Qdrant collection population
7. 9.7 Create documentation
---
Proceeding with implementation:<tool_call>write<arg_key>content</arg_key><arg_value># Singapore SMB Customer Support - FAQ
Last Updated: December 2025
General Questions
Account & Security
Q: How do I create an account?
A: You can create an account by clicking the "Register" button on our chat interface. Simply provide your email address and create a password. Your data is protected under Singapore's Personal Data Protection Act (PDPA), and you can delete your account at any time.
Q: How is my personal data protected?
A: We take your privacy seriously. All personal data is stored securely and automatically expires after 30 days. We comply with Singapore's Personal Data Protection Act (PDPA) regulations.
Q: Can I delete my account?
A: Yes, you can request account deletion at any time. All your personal data will be permanently removed from our systems within 30 days as required by PDPA.
Business Hours
Q: What are your support hours?
A: Our customer support team is available Monday through Friday, 9:00 AM to 6:00 PM Singapore Time (GMT+8). We are closed on weekends and Singapore public holidays.
Q: Are you available on weekends?
A: Currently, our customer support operates on weekdays only. Weekend support is not available, but you can still leave a message outside business hours and we will respond on the next business day.
Q: What happens on public holidays?
A: We observe all Singapore public holidays. On these days, our support team is unavailable. Messages sent during public holidays will be responded to on the next business day.
Services
Q: What services do you offer?
A: We offer comprehensive customer support services including:
- Product information and recommendations
- Order status and tracking
- Technical support and troubleshooting
- Billing and payment inquiries
- Returns and refund assistance
- Account management support
Q: Do you offer technical support?
A: Yes, we provide technical support for all our products. This includes installation assistance, troubleshooting guides, and warranty claims. Our support team can help diagnose issues and provide solutions.
Q: Can you help with order tracking?
A: Absolutely. You can ask us about your order status anytime. Simply provide your order number, and we'll check the latest tracking information and estimated delivery date.
Pricing & Payments
Q: What payment methods do you accept?
A: We accept all major payment methods including:
- Credit/Debit Cards (Visa, Mastercard, American Express)
- PayNow (Singapore's unified payment method)
- Bank Transfer
- GrabPay
Q: Do you offer discounts for businesses?
A: Yes, we offer special pricing for our business customers. Contact our sales team at sales@singapoersmb.com for more information about our B2B pricing tiers.
Q: Are there any additional fees?
A: We maintain transparent pricing. The prices you see are the prices you pay. There are no hidden fees or surprise charges. Standard shipping fees apply to all orders.
Shipping & Delivery
Q: What are your shipping options?
A: We offer several shipping options to meet your needs:
- Standard Delivery: 3-5 business days
- Express Delivery: 1-2 business days
- Same Day Delivery: Available for orders placed before 12 PM (additional fee)
- Self-Pickup: Available from our Singapore store
Q: Do you ship internationally?
A: Currently, we only ship within Singapore. International shipping is not available at this time.
Q: How do I track my order?
A: You can track your order by:
- Using the tracking number sent to your email
- Checking your order status in our chat support
- Logging into your account to view order history
Q: What happens if my package is delayed?
A: If your package delivery is delayed beyond the estimated timeframe, please contact our support team. We will investigate the delay and provide you with updated information or arrange for a replacement if necessary.
Returns & Refunds
Q: What is your return policy?
A: We offer a 30-day return policy for most items. Products must be in original condition with tags attached. Some items such as personalized products or final sale items are not eligible for return.
Q: How do I return an item?
A: To return an item:
1. Contact our support team within 30 days of purchase
2. Provide your order number and reason for return
3. We will provide you with a return authorization number
4. Pack the item securely with all original packaging
5. Send to our returns center or arrange for pickup
Q: How long do refunds take to process?
A: Refunds are typically processed within 5-7 business days after we receive your returned item. You will receive confirmation email once the refund has been processed.
Q: Can I return sale items?
A: Final sale items are not eligible for return unless they are defective. Please check product descriptions carefully before purchasing sale items.
Product Information
Q: Where can I find product specifications?
A: Product specifications are available on our website and can also be obtained through this chat support. Ask our AI agent about any specific product, and we'll provide detailed specifications.
Q: Do your products come with warranty?
A: Yes, all our products come with manufacturer warranty. Warranty periods vary by product type. Contact support for specific warranty information about your product.
Q: Are your products tested for quality?
A: Absolutely. All products undergo rigorous quality testing before shipping. We work with reputable suppliers and brands to ensure product reliability and customer satisfaction.
Technical Support
Q: I'm having trouble with my product. What should I do?
A: First, try our self-help resources:
1. Check product documentation (available on our website)
2. Browse our FAQ section for common issues
3. Watch our video tutorials for setup guides
If these don't resolve your issue, contact our support team with details about the problem you're experiencing.
Q: Do you offer setup or installation services?
A: For certain products, we offer professional installation services in Singapore. Contact our sales team for information about installation options and pricing.
Contact Us
Q: How can I reach a human agent?
A: If you need to speak with a human agent, you can request this through our chat interface. During business hours, we'll connect you with a support representative within 2-3 minutes. Outside business hours, we'll respond on the next business day.
Q: What information should I have ready when contacting support?
A: To help us assist you more efficiently, please have ready:
- Your account email address
- Order number (if applicable)
- Product name or model number
- Clear description of your issue or question
- Screenshots or photos (if applicable, for technical issues)
Q: Is there a preferred time to contact support?
A: For faster response times, we recommend contacting us during our business hours (Monday-Friday, 9 AM - 6 PM SGT). Queries sent during business hours are typically responded to within 15-30 minutes.
Escalation
Q: What happens if my issue can't be resolved through chat?
A: If your issue requires specialized handling or cannot be resolved through chat, our support agent will escalate your case to our senior support team or relevant department (technical, billing, etc.) and create a support ticket for you. You'll receive a ticket ID for tracking purposes.
Q: How do I check the status of my support ticket?
A: You can check your support ticket status by providing your ticket ID to our support agent. Our team will provide you with updates as your case progresses.
---
Need more help? Contact our AI support agent anytime, or reach a human agent during business hours (Mon-Fri, 9 AM - 6 PM SGT).
</arg_value><arg_key>filePath</arg_key><arg_value>/home/project/ai-agent/backend/data/faq/pricing_payments.md</arg_value></tool_call>
