const addCommentForm = document.getElementById('add-comment-form');
const newCommentContainer = document.getElementById('new-comment-container');

// Get the existing comments from local storage
let comments = JSON.parse(localStorage.getItem('comments')) || [];

addCommentForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const commentHeader = document.getElementById('comment-header').value;
  const commentContent = document.getElementById('comment-content').value;
  let userName = "test";
  if (!localStorage.getItem("user")) {
    alert("Please login to add a comment");
  } else {
    userName = localStorage.getItem("user");
  }

  // Create a new comment object
  const newComment = {
    header: commentHeader,
    content: commentContent,
    username: userName
  };

  // Add the new comment to the array
  comments.push(newComment);

  // Save the comments to local storage
  localStorage.setItem('comments', JSON.stringify(comments));

  // Append the new comment to the new comment container
  const newCommentHTML = `
          <div class="col-md-6">
            <div class="card mb-3">
              <div class="card-body">
                <h5 class="card-title">${commentHeader}</h5>
                <p class="card-text">${commentContent}</p>
                <p class="card-text">Posted by: <a href="#">@${userName.toLowerCase()}</a></p>
              </div>
            </div>
          </div>
        `;
  newCommentContainer.innerHTML += newCommentHTML;

  document.getElementById('comment-header').value = '';
  document.getElementById('comment-content').value = '';
});

// Load comments from local storage and append to new comment container
function loadComments() {
  comments = JSON.parse(localStorage.getItem('comments')) || [];
  newCommentContainer.innerHTML = '';
  comments.forEach((comment) => {
    const commentHTML = `
            <div class="col-md-6">
              <div class="card mb-3">
                <div class="card-body">
                  <h5 class="card-title">${comment.header}</h5>
                  <p class="card-text">${comment.content}</p>
                  <p class="card-text">Posted by: <a href="#">@${comment.username.toLowerCase()}</a></p>
                </div>
              </div>
            </div>
          `;
    newCommentContainer.innerHTML += commentHTML;
  });
}

// Load comments on page load
loadComments();