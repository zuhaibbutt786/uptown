document.getElementById("uploadForm").addEventListener("submit", async function (event) {
    event.preventDefault();
    
    let formData = new FormData();
    formData.append("projectName", document.getElementById("projectName").value);
    formData.append("file", document.getElementById("fileUpload").files[0]);

    document.getElementById("statusMessage").innerText = "Uploading...";

    try {
        let response = await fetch("http://localhost:5000/upload", {
            method: "POST",
            body: formData
        });

        let result = await response.json();
        document.getElementById("statusMessage").innerText = result.message;
    } catch (error) {
        document.getElementById("statusMessage").innerText = "Error uploading project.";
    }

//     async function fetchProject(projectName) {
//     try {
//         const response = await fetch(`/project/${projectName}`, {
//             method: 'GET',
//             headers: {
//                 'Content-Type': 'application/json'
//             }
//         });

//         if (!response.ok) {
//             throw new Error(`Error: ${response.status} ${response.statusText}`);
//         }

//         const data = await response.json();
//         console.log("Project Data:", data);
//         return data;
//     } catch (error) {
//         console.error("Failed to fetch project:", error);
//     }
// }

// Example usage
fetchProject("my_project");

});
