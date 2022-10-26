<?php
/**
 * IPP 2022 project (first part) 
 * @author Rastislav Duránik (xduran03)
 * 15.3.2022
 */

# Stderr error output
ini_set('display_errors', 'stderr');

# Defines
define('ERR_OK', 0);
define('ERR_ARGUMENTS', 10);
define('ERR_INPUT_FILE', 11);
define('ERR_OUTPUT_FILE', 12);
define('ERR_MISSING_HEADER', 21);
define('ERR_WRONG_CODE', 22);
define('ERR_OTHER', 23);

# XML settings
$dom_tree = new DOMDocument('1.0', 'UTF-8');
$dom_tree->formatOutput = true;
$xml_Root = $dom_tree->createElement("program");
$xml_Root->setAttribute("language", "IPPcode22");
$xml_Root = $dom_tree->appendChild($xml_Root);

# Global variables
$header = false;
$file_read = false;
$instruction_count = 1;

# Argument verification
arg_check($argc,$argv);

# Reading line by line from STDIN file
while ($line = fgets(STDIN)){ 

    $file_read = true;
    
    # Creates element instruction
    $xmlInstruction = $dom_tree->createElement("instruction");
    $xmlInstruction->setAttribute("order", $instruction_count); 
    
    # Check if the sentence is comment/newline
    if (preg_match('~^\s*#~', $line) || preg_match('~^\s*$~', $line)) {
        continue;
    }

    # If there is comment on line ignore everything after comment
    $split_comment = explode('#', $line);     
    
    # Checking if code contains valid header
    if(!$header){

        $header_check = strtoupper($split_comment[0]);    
        
        if(strcmp(trim($header_check), ".IPPCODE22") == 0){ 

            $header = true;
            continue;
        }
        else{ 

            fwrite(STDERR, "Error: missing/incorrect header");
            exit(ERR_MISSING_HEADER);
        }
    } 
    
    # Splits line into arr trough delimiter >> " " 
    $splitted = explode(' ', trim($split_comment[0])); 

    # Syntax/Lexical control trought instruction switch
    switch(strtoupper($splitted[0])){        

        # intructions without operand
        case 'CREATEFRAME':
        case 'PUSHFRAME': 
        case 'POPFRAME': 
        case 'RETURN':
        case 'BREAK':
            
            # cant contain any operand 
            if (count($splitted) != 1) {                
                fwrite(STDERR, "Error: Lexical/Syntax error");
                exit(ERR_OTHER);
            }
            # setting opcode attribute
            $xmlInstruction->setAttribute("opcode", $splitted[0]);
                      
            break;

        # one var operand    
        case 'DEFVAR':
        case 'POPS':
            
            # must have 1 operand
            if (count($splitted) == 2) {  

                # setting opcode attribute
                $xmlInstruction->setAttribute("opcode", $splitted[0]);
                # calling function to check variable syntax
                if (var_check($splitted[1])){
                    # sets first arg element
                    $xmlArg1 = $dom_tree->createElement("arg1", htmlspecialchars($splitted[1]));
                    $xmlArg1->setAttribute("type", "var");
                    # sets arg1 element as an instruction child
                    $xmlInstruction->appendChild($xmlArg1);
                } 
                else{
                    fwrite(STDERR, "Error: Lexical/Syntax error");
                    exit(ERR_OTHER);
                }                                
            }
            else {
                fwrite(STDERR, "Error: Lexical/Syntax error");
                exit(ERR_OTHER);
            }                  
            break;

        # one constant or var operand 
        case 'PUSHS':  
        case 'WRITE':
        case 'DPRINT':
        case 'EXIT':
            
            # must have 1 operand
            if (count($splitted) == 2) {  
                
                # setting opcode attribute
                $xmlInstruction->setAttribute("opcode", $splitted[0]);  
                # determining whether it is variable or constant
                if (VarVSConst($splitted[1])){

                    $xmlArg1 = $dom_tree->createElement("arg1", htmlspecialchars($splitted[1]));
                    $xmlArg1->setAttribute("type", "var");
                }                
                else{
                    
                    # splits const to get it's type
                    $split_const = explode('@', $splitted[1],2);
                    # Sets arg element
                    $xmlArg1 = $dom_tree->createElement("arg1", htmlspecialchars($split_const[1]));
                    $xmlArg1->setAttribute("type", $split_const[0]); 
                }
                # sets arg elements as an instruction child
                $xmlInstruction->appendChild($xmlArg1);
                
            }
            else {
                fwrite(STDERR, "Error: Lexical/Syntax error");
                exit(ERR_OTHER);
            }                  
            break;
            

        # One label operand
        case 'CALL':
        case 'LABEL':
        case 'JUMP':

            if (count($splitted) == 2) {  

                # setting opcode attribute
                $xmlInstruction->setAttribute("opcode", $splitted[0]);
                # calling function to check label syntax
                if (label_check($splitted[1])){
                    # Sets arg element
                    $xmlArg1 = $dom_tree->createElement("arg1", htmlspecialchars($splitted[1]));
                    $xmlArg1->setAttribute("type", "label");
                    # sets arg elements as an instruction child
                    $xmlInstruction->appendChild($xmlArg1);
                }                               
            }
            else {
                fwrite(STDERR, "Error: Lexical/Syntax error");
                exit(ERR_OTHER);
            }                        
            break;
            

        # one var operand and one constant or var operand
        case 'MOVE':
        case 'NOT':
        case 'INT2CHAR':
        case 'STRLEN':
        case 'TYPE':

            if (count($splitted) == 3) { 

                # setting opcode attribute
                $xmlInstruction->setAttribute("opcode", $splitted[0]);
                # calling function to check variable syntax
                if (var_check($splitted[1])){
                    # sets arg element
                    $xmlArg1 = $dom_tree->createElement("arg1", htmlspecialchars($splitted[1]));
                    $xmlArg1->setAttribute("type", "var");
                    # sets arg elements as an instruction child
                    $xmlInstruction->appendChild($xmlArg1);

                    # determining whether it is variable or constant
                    if (VarVSConst($splitted[2])){

                        $xmlArg2 = $dom_tree->createElement("arg2", htmlspecialchars($splitted[2]));
                        $xmlArg2->setAttribute("type", "var");
                    }
                    else{

                        # splits const to get it's type
                        $split_const = explode('@', $splitted[2],2);
                        $xmlArg2 = $dom_tree->createElement("arg1", htmlspecialchars($split_const[1]));
                        $xmlArg2->setAttribute("type", $split_const[0]); 
                    }
                    # sets arg elements as an instruction child
                    $xmlInstruction->appendChild($xmlArg2);                    
                }
                else {
                    fwrite(STDERR, "Error: Lexical/Syntax error");
                    exit(ERR_OTHER);
                }

            }
            else {
                fwrite(STDERR, "Error: Lexical/Syntax error");
                exit(ERR_OTHER);
            }                        
            break;           

        # one var operand and one type operand
        case 'READ':
            
            if (count($splitted) == 3) { 
                
                # setting opcode attribute
                $xmlInstruction->setAttribute("opcode", $splitted[0]);
                
                if (var_check($splitted[1])){
                    # sets arg element
                    $xmlArg1 = $dom_tree->createElement("arg1", htmlspecialchars($splitted[1]));
                    $xmlArg1->setAttribute("type", "var");
                    # sets arg elements as an instruction child
                    $xmlInstruction->appendChild($xmlArg1);

                    if (type_check($splitted[2])){
                        # sets arg element
                        $xmlArg2 = $dom_tree->createElement("arg2", htmlspecialchars($splitted[2]));
                        $xmlArg2->setAttribute("type", "type");
                        # sets arg elements as an instruction child
                        $xmlInstruction->appendChild($xmlArg2);
                    }
                }
                else {
                    fwrite(STDERR, "Error: Lexical/Syntax error");
                exit(ERR_OTHER);
                }                
            }
            else {
                fwrite(STDERR, "Error: Lexical/Syntax error");
                exit(ERR_OTHER);
            }                        
            break;

        # One var operand and two constant or var operand
        case 'ADD':
        case 'SUB':    
        case 'MUL':    
        case 'IDIV':   
        case 'LT':    
        case 'GT':    
        case 'EQ':    
        case 'AND':    
        case 'OR':
        case 'STRI2INT':
        case 'CONCAT':
        case 'GETCHAR':
        case 'SETCHAR':
            
            if (count($splitted) == 4) {  
                
                # setting opcode attribute
                $xmlInstruction->setAttribute("opcode", $splitted[0]);
                
                if (var_check($splitted[1])){
                    # sets arg element
                    $xmlArg1 = $dom_tree->createElement("arg1", htmlspecialchars($splitted[1]));
                    $xmlArg1->setAttribute("type", "var");
                    # sets arg elements as an instruction child
                    $xmlInstruction->appendChild($xmlArg1);

                    # determining whether it is variable or constant
                    if (VarVSConst($splitted[2])){

                        $xmlArg2 = $dom_tree->createElement("arg2", htmlspecialchars($splitted[2]));
                        $xmlArg2->setAttribute("type", "var");                        
                    }
                    else{
                        # Cuts constant using @ as delimiter
                        $split_const = explode('@', $splitted[2],2);
                        $xmlArg2 = $dom_tree->createElement("arg2", htmlspecialchars($split_const[1]));
                        $xmlArg2->setAttribute("type", $split_const[0]);
                    }
                    # sets arg elements as an instruction child
                    $xmlInstruction->appendChild($xmlArg2);
                    if (VarVSConst($splitted[3])){

                        $xmlArg3 = $dom_tree->createElement("arg3", htmlspecialchars($splitted[3]));
                        $xmlArg3->setAttribute("type", "var");
                    }
                    else{
                        # Cuts constant using @ as delimiter
                        $split_const = explode('@', $splitted[3],2);
                        $xmlArg3 = $dom_tree->createElement("arg3", htmlspecialchars($split_const[1]));
                        $xmlArg3->setAttribute("type", $split_const[0]);
                    }
                    # sets arg elements as an instruction child
                    $xmlInstruction->appendChild($xmlArg3);                    
                }
                else {
                    fwrite(STDERR, "Error: Lexical/Syntax error");
                    exit(ERR_OTHER);
                }
                
            }
            else {
                fwrite(STDERR, "Error: Lexical/Syntax error");
                exit(ERR_OTHER);
            }                     
            break;     

        # one label operand and two constant or var operand
        case 'JUMPIFEQ':
        case 'JUMPIFNEQ':       
            
            if (count($splitted) == 4) { 
                
                # setting opcode attribute
                $xmlInstruction->setAttribute("opcode", $splitted[0]);
                
                if (label_check($splitted[1])){
                    # Sets arg element
                    $xmlArg1 = $dom_tree->createElement("arg1", htmlspecialchars($splitted[1]));
                    $xmlArg1->setAttribute("type", "label");
                    # sets arg elements as an instruction child
                    $xmlInstruction->appendChild($xmlArg1);

                    # determining whether it is variable or constant
                    if (VarVSConst($splitted[2])){

                        $xmlArg2 = $dom_tree->createElement("arg2", htmlspecialchars($splitted[2]));
                        $xmlArg2->setAttribute("type", "var");                        
                    }
                    else{
                        # Cuts constant using @ as delimiter
                        $split_const = explode('@', $splitted[2],2);
                        $xmlArg2 = $dom_tree->createElement("arg2", htmlspecialchars($split_const[1]));
                        $xmlArg2->setAttribute("type", $split_const[0]);
                    }
                    # sets arg elements as an instruction childv
                    $xmlInstruction->appendChild($xmlArg2);
                    if (VarVSConst($splitted[3])){

                        $xmlArg3 = $dom_tree->createElement("arg3", htmlspecialchars($splitted[3]));
                        $xmlArg3->setAttribute("type", "var");
                    }
                    else{
                        # Cuts constant using @ as delimiter
                        $split_const = explode('@', $splitted[3],2);
                        $xmlArg3 = $dom_tree->createElement("arg3", htmlspecialchars($split_const[1]));
                        $xmlArg3->setAttribute("type", $split_const[0]);
                    }
                    # sets arg elements as an instruction child
                    $xmlInstruction->appendChild($xmlArg3);                     
                }                
            }
            else {
                fwrite(STDERR, "Error: Instruction error");
                exit(ERR_WRONG_CODE);
            }                        
            break;
    }
    $xml_Root->appendChild($xmlInstruction);
    # Increases count of intructions amount
    $instruction_count++;
}

if (!$file_read){
    fwrite(STDERR, "Error: Failed to open input file");
    exit(ERR_INPUT_FILE);
}


echo $dom_tree->saveXML();

exit(ERR_OK);

# Function veryfies arguments
function arg_check($argc,$argv){
    #checking arguments
    if ($argc == 2)
    {
        # help/usage info
        if($argv[1] == "--help"){        
            echo("Usage: parser.php [--help (optional)] <inputFile")."\n";
            exit(ERR_OK);
        }
        else{
            fwrite(STDERR, "Error : invalid arguments");
            exit(ERR_ARGUMENTS);
        }
    }else if ($argc > 2){
        fwrite(STDERR, "Error : invalid arguments");
        exit(ERR_ARGUMENTS); 
    }   
    
}

# Fuction validates variable using regular expression
function var_check($string_to_test){

    if (preg_match("~^(LF|TF|GF)@[a-zA-Z_%$-&?!*][a-zA-Z0-9_%$-&?!*]*$~", $string_to_test)) {
        return true;
    }       
}

# Fuction validates constant using regular expression
function constant_check($string_to_test){

    if (preg_match("~^int@[+-]?[0-9]+$~", $string_to_test) ||
                    preg_match("~^bool@(true|false)$~", $string_to_test) ||
                    preg_match("~^string@~", $string_to_test) ||
                    preg_match("~^nil@nil~", $string_to_test)) {
        return true;
    }       
}

# Fuction validates label using regular expression
function label_check($string_to_test){
    
    if (preg_match("~^[a-zA-Z_%$-&?!*][a-zA-Z0-9_%$-&?!*]*$~", $string_to_test)){
        return true;
    }
    else{
        fwrite(STDERR, "Error: Lexical/Syntax error");
        exit(ERR_OTHER);
    }   
}

# Fuction validates type using regular expression
function type_check($string_to_test){
    
    if (preg_match("~^(int|bool|string)$~", $string_to_test)){
        return true;
    }
    else{
        fwrite(STDERR, "Error: Lexical/Syntax error");
        exit(ERR_OTHER);
    }   
}

# Function determines whether token has variable or const value
function VarVSConst($string_to_test){
    
    # determining whether it is variable or constant
    if (var_check($string_to_test)){

        # if var true
        return true;
    }
    else if (constant_check($string_to_test)){

        # if const false
        return false;
    }
    else{

        fwrite(STDERR, "Error: Lexical/Syntax error");
        exit(ERR_OTHER);
    }  
}

 



?>