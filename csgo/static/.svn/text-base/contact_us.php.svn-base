<?php
//If the form is submitted
error_reporting(E_ALL);
$response = array();
if(count($_POST) > 0) {
	$comments = $_POST['message'];

	//Check to make sure that the name field is not empty
	if(trim($_POST['name']) == '') {
		$hasError = true;
	} else {
		$name = trim($_POST['name']);
	}


	//Check to make sure sure that a valid email address is submitted
	if(trim($_POST['email']) == '')  {
		$hasError = true;
	} else if (!eregi("^[A-Z0-9._%-]+@[A-Z0-9._%-]+\.[A-Z]{2,4}$", trim($_POST['email']))) {
		$hasError = true;
	} else {
		$email = trim($_POST['email']);
	}

	$website = trim($_POST['website']);

	//If there is no error, send the email

	if(!isset($hasError)) {
		$emailTo = 'mail@company.com'; //Put your own email address here
		$body = "Name: $name \n\nEmail: $email \n\nWebsite: $website \n\nComments:\n $comments";
		$headers = 'From: My Site: '. $emailTo . "\r\n" . 'Reply-To: ' . $email;

		mail($emailTo, 'Glocal', $body, $headers);
		$emailSent = true;
		$response['message'] = "Thank you! Email successfully sent.";

	}else{
	    $response['message'] = "Please check if you've filled all the fields with valid information. Thank you.";
	}
	echo json_encode($response);
}else{
    echo json_encode(array('message'=>"Please check if you've filled all the fields with valid information. Thank you."));
}
?>