# 확인한 근거

확인일: 2026년 11월 3일. 문서 설명과 로컬 관찰은 실제 변환 성공을 의미하지 않는다.

| ID | 출처와 관찰 | 뒷받침하는 결정과 한계 |
| --- | --- | --- |
| S01 | [OCRmyPDF 공식 문서](https://ocrmypdf.readthedocs.io/en/latest/): 스캔 PDF에 OCR 텍스트 레이어 추가 | 검색형 PDF 후보. 이 프로젝트 설치/변환은 아직 미실행 |
| S02 | [Tesseract 공식 CLI 안내](https://tesseract-ocr.github.io/tessdoc/Command-Line-Usage.html): 언어 지정·여러 언어 사용과 출력 형식 설명 | 한영 처리 후보. 모든 문자의 정확도를 보장하지 않음 |
| S03 | [Tesseract 품질 안내](https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html): 이미지 품질·기울기·분할 방식 등이 OCR에 영향 | 복잡 배치·저품질 별도 검증 필요 |
| E01 | 이 세션 PATH에서 Tesseract·pdftotext 발견, 언어팩 eng/kor/osd 확인 | 로컬 기초 도구 존재. 변환 제품 구현 증거 아님 |
| E02 | 이 세션 Python에서 PIL 발견, OCRmyPDF/pypdf/reportlab/fitz 미발견 | 프로젝트 가상환경·의존성 설치 여부를 개발 때 판단 |
| E03 | Herdr app/core 내장 명령으로 현재 공간/터미널 조회 성공 | 실제 문서 인수·협업은 별도 PILOT 결과로 판단 |

시험지 품질·수요·정확도·처리 속도를 측정한 데이터는 아직 없다. 실제 측정이 생기면 입력 해시와 환경을 함께 추가한다.
