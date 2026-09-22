"use client";

import { ChangeEvent, FormEvent, useEffect, useState } from "react";

export default function Home() {
  const [image, setImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [resultUrl, setResultUrl] = useState<string | null>(null);

  const [searchPrompt, setSearchPrompt] = useState("");
  const [prompt, setPrompt] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }

      if (resultUrl) {
        URL.revokeObjectURL(resultUrl);
      }
    };
  }, [previewUrl, resultUrl]);

  const handleImageChange = (
    event: ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (!file.type.startsWith("image/")) {
      setError("Vui lòng chọn một file ảnh.");
      return;
    }

    setImage(file);
    setError("");

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    const newPreviewUrl = URL.createObjectURL(file);
    setPreviewUrl(newPreviewUrl);

    if (resultUrl) {
      URL.revokeObjectURL(resultUrl);
      setResultUrl(null);
    }
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    if (!image) {
      setError("Vui lòng chọn ảnh trước.");
      return;
    }

    if (!searchPrompt.trim()) {
      setError("Vui lòng nhập đối tượng cần chỉnh sửa.");
      return;
    }

    if (!prompt.trim()) {
      setError("Vui lòng nhập yêu cầu chỉnh sửa.");
      return;
    }

    setLoading(true);
    setError("");
    setResultUrl(null);

    try {
      const formData = new FormData();

      formData.append("image", image);
      formData.append("search_prompt", searchPrompt);
      formData.append("prompt", prompt);

      const response = await fetch(
        "http://127.0.0.1:8000/api/images/edit",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        let message = "Không thể chỉnh sửa ảnh.";

        try {
          const data = await response.json();

          if (data.detail) {
            message = data.detail;
          }
        } catch {
          // Response không phải JSON
        }

        throw new Error(message);
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);

      setResultUrl(url);
    } catch (error) {
      console.error(error);

      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Đã xảy ra lỗi không xác định.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!resultUrl) {
      return;
    }

    const link = document.createElement("a");

    link.href = resultUrl;
    link.download = "aipicture-result.png";

    link.click();
  };

  return (
    <main className="page">
      <div className="container">

        <header className="header">
          <h1>AIPicture</h1>

          <p>
            AI Image Editing
          </p>
        </header>


        <section className="editor">

          {/* LEFT - UPLOAD */}

          <div className="upload-section">

            <label
              htmlFor="image-upload"
              className="upload-box"
            >

              {previewUrl ? (

                <img
                  src={previewUrl}
                  alt="Ảnh đã chọn"
                  className="preview-image"
                />

              ) : (

                <div className="upload-placeholder">

                  <div className="upload-icon">
                    +
                  </div>

                  <h2>
                    Chọn ảnh
                  </h2>

                  <p>
                    JPG, PNG hoặc WebP
                  </p>

                </div>

              )}

            </label>


            <input
              id="image-upload"
              type="file"
              accept="image/png,image/jpeg,image/webp"
              onChange={handleImageChange}
              hidden
            />

          </div>


          {/* RIGHT - CONTROLS */}

          <form
            onSubmit={handleSubmit}
            className="control-section"
          >

            {/* SEARCH PROMPT */}

            <div className="field">

              <label htmlFor="search-prompt">
                Đối tượng cần chỉnh sửa
              </label>

              <input
                id="search-prompt"
                type="text"
                value={searchPrompt}
                onChange={(event) =>
                  setSearchPrompt(event.target.value)
                }
                placeholder="Ví dụ: car, person, tree, chair..."
              />

              <p className="field-hint">
                Nhập đối tượng hoặc khu vực bạn muốn thay đổi
              </p>

            </div>


            {/* PROMPT */}

            <div className="field">

              <label htmlFor="prompt">
                Bạn muốn chỉnh sửa gì?
              </label>

              <textarea
                id="prompt"
                value={prompt}
                onChange={(event) =>
                  setPrompt(event.target.value)
                }
                placeholder="Ví dụ: Change the car color to blue..."
                rows={7}
              />

            </div>


            {error && (
              <div className="error">
                {error}
              </div>
            )}


            <button
              type="submit"
              className="generate-button"
              disabled={loading}
            >

              {loading
                ? "Đang chỉnh sửa..."
                : "Chỉnh sửa ảnh"}

            </button>

          </form>

        </section>


        {/* RESULT */}

        {resultUrl && (

          <section className="result-section">

            <div className="result-header">

              <div>

                <h2>
                  Kết quả
                </h2>

                <p>
                  Ảnh được tạo bởi Stability AI
                </p>

              </div>


              <button
                onClick={handleDownload}
                className="download-button"
              >
                Tải ảnh xuống
              </button>

            </div>


            <div className="result-image-container">

              <img
                src={resultUrl}
                alt="Ảnh kết quả"
                className="result-image"
              />

            </div>

          </section>

        )}

      </div>
    </main>
  );
}