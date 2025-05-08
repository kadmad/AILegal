run:
	uvicorn app.main:app --reload

dev-refresh:
	docker compose up gateway --build -d

ocr-refresh:
	docker compose up ocr_extraction --build -d

summary-refresh:
	docker compose up summary --build -d