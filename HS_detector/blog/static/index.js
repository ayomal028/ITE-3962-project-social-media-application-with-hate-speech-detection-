
function like(postId){
    const likeCount =  document.getElementById(`likes-count-${postId}`);
    const likeButton = document.getElementById(`likes-button-${postId}`);

    fetch(`/like-post/${postId}`, {method: "POST"})
        .then((res) => res.json())
        .then((data) => {
            likeCount.innerHTML = data["likes"];

            if(data["liked"]){
                likeButton.className = "fa-solid fa-thumbs-up fa-2x";
            }
            else{
                likeButton.className = "fa-regular fa-thumbs-up fa-2x";
            }
            
        }).catch((e) => alert("could not like the post"));


}