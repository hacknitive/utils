HTML_PAGE_FOR_404 = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>404 - Page Not Found | X50.ir</title>
  <style>
    /* Reset Styles */
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    /* Body Styles */
    body {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      background-color: #f9f9f9;
      color: #333;
      padding: 20px;
    }

    /* Main Container */
    .container {
      text-align: center;
      max-width: 600px;
      padding: 20px;
      border: 1px solid #dedede;
      border-radius: 8px;
      background-color: #fff;
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }

    /* 404 header styling */
    h1 {
      font-size: 6rem;
      color: #e74c3c;
      margin-bottom: 20px;
    }

    /* Message styling */
    p {
      font-size: 1.2rem;
      margin-bottom: 20px;
      line-height: 1.5;
    }

    /* Link Button styling */
    a.button {
      display: inline-block;
      text-decoration: none;
      color: #fff;
      background-color: #3498db;
      padding: 12px 24px;
      border-radius: 4px;
      transition: background-color 0.3s ease;
    }

    a.button:hover {
      background-color: #2980b9;
    }

    /* Domain style */
    .domain {
      font-weight: bold;
      color: #3498db;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>404</h1>
    <p>
      Oops! The page you're looking for doesn't exist.
    </p>
    <p>
      It seems you've hit a dead end on <span class="domain">X50.ir</span>.
      Please check the URL.
    </p>
  </div>
  <script>
    // Optional: Auto-redirect after 10 seconds
    // Uncomment the code below to enable automatic redirection
    //
    // setTimeout(function () {
    //   window.location.href = "/";
    // }, 10000);

    // Log information in the console
    console.log("404 Page - Page not found on X50.ir");
  </script>
</body>
</html>"""