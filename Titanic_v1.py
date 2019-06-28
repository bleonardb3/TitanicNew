import urllib3, requests, json, os
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, FloatField, IntegerField
from wtforms.validators import Required, Length, NumberRange

#url = 'https://us-south.ml.cloud.ibm.com'
#username = '30157a36-5b6b-4fbc-b65f-634e5c97a628'
#password = '5c2e95cf-fce9-4a82-bbba-b7024a716322'

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'pm-20' in vcap:
        creds = vcap['pm-20'][0]['credentials']
        username = creds['username']
        password = creds['password']
        url = creds['url']
scoring_endpoint = 'https://us-south.ml.cloud.ibm.com/v4/deployments/91019be5-095c-4bbf-bc1c-77bb9a1fc20e/predictions'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretpassw0rd'
bootstrap = Bootstrap(app)
class TitanicForm(FlaskForm):
  pclass = RadioField('Passenger Class:', coerce=str, choices=[('1','First'),('2','Second'),('3','Third')])
  sex = RadioField('Gender:', coerce=str, choices=[('male','Male'),('female','Female')])
  age = StringField('Age:')
  fare = StringField('Fare:')
  sibsp = StringField('Number of siblings/spouses:')
  parch = StringField('Number of parents/children:')
  embarked = RadioField('Embark Location:', coerce=str, choices=[('S','South Hampton'),('C','Cherbourg'),('Q','Queenstown')])
  submit = SubmitField('Submit')
@app.route('/', methods=['GET', 'POST'])
def index():
  form = TitanicForm()
  if form.is_submitted(): 
    sex = form.sex.data
    print (sex)
    form.sex.data = ''
    age = form.age.data
    print (age)
    form.age.data = ''
    pclass = form.pclass.data
    form.pclass.data = ''
    fare = form.fare.data
    form.fare.data = '' 
    sibsp = form.sibsp.data
    form.sibsp.data = ''
    parch = form.parch.data
    form.parch.data = ''   
    embarked = form.embarked.data
    form.embarked.data = ''    
    
    headers = urllib3.util.make_headers(basic_auth='{}:{}'.format(username, password))
    path = '{}/v3/identity/token'.format(url)
    response = requests.get(path, headers=headers)
    mltoken = json.loads(response.text).get('token')
    scoring_header = {'Content-Type': 'application/json', 'Authorization': 'Bearer' + mltoken}
    payload = {"input_data": [{"fields": ["pclass","sex","age","sibsp","parch","fare","embarked"], "values": [[pclass,sex,age,sibsp,parch,fare,embarked]]}]}
    print("payload:",payload)
    scoring = requests.post(scoring_endpoint, json=payload, headers=scoring_header)

    scoringDICT = json.loads(scoring.text) 
    print("scoringDICT:",scoringDICT)
    scoringList = scoringDICT['predictions'][0]['values']
    print (scoringList)
    score = scoringList[0][0]
    probability_died = scoringList[0][1][0]
    print (probability_died)
    probability_survived = scoringList[0][1][1]
    if (score == 1.0) :
      score_str = "survived"
      probability = probability_survived                                        
    else :
      score_str = "did not survive"
      probability = probability_died
      
    #probability = scoringList[6:7].pop()[0:1].pop()

    return render_template('score.html', form=form, scoring=score_str,probability=probability)
  return render_template('index.html', form=form)
port = os.getenv('PORT', '5000')
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=int(port))
