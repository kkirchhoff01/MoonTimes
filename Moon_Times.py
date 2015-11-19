##########################################################################
#                                                                        #
#    All data taken belongs to aa.usno.navy.mil                          #
#                                                                        #
#    This class retrieves the position of the Moon during a given period #
#    and parses the data to find the optimal positions and their         #
#    corresponding times/dates for a Moon bounce.                        #
#                                                                        #
#    Requires the mechanize python module                                #
#                                                                        #
##########################################################################

import urllib
import urllib2
import mechanize
from datetime import date

class Moon_Times():
	def __init__(self):
		self.url = "http://aa.usno.navy.mil/data/docs/AltAz.php"
		#Create/open file to store moon data pages
		self.br = mechanize.Browser()
		self.br.set_handle_robots(False)

	#Gets the moon data page
	def getPage(self,xxm, xxd, xxy, tz, location):
		#Opens form page
		self.br.open(self.url)
		self.br.select_form(nr=2)
		print "Getting data for " + xxm + "/"+ xxd + "/"+ xxy

		#Form data
		self.br.form["body"] = ["11",]
		self.br["day"] = xxd
		self.br["year"] = xxy
		self.br["month"] = [xxm,]
		self.br["intv_mag"] = "1"
		
		#Form data for the Long Wavelength Array
		if location == 'LWA':	
			self.br["place"] = "LWA, New Mexico"
			self.br.form["lon_sign"] = ["-1",]
			self.br["lon_deg"] = "107"
			self.br["lon_min"] = "37"
			self.br.form["lat_sign"] = ["1",]
			self.br["lat_deg"] = "34"
			self.br["lat_min"] = "04"
			#Time zone (+7 West of Greenwich)
			self.br["tz"] = tz
			self.br.form["tz_sign"] = ["-1",]

		#Form data for the TARA transmitter
		elif location == 'TARA':
			#Entries for coordinate form
			self.br["place"] = "Delta, UT Transmitter"
			self.br.form["lon_sign"] = ["-1",]
			self.br["lon_deg"] = "112"
			self.br["lon_min"] = "42"
			self.br.form["lat_sign"] = ["1",]
			self.br["lat_deg"] = "39"
			self.br["lat_min"] = "20"
			#Time zone (+7 West of Greenwich)
			self.br["tz"] = tz
			self.br.form["tz_sign"] = ["-1",]
	
		else:
			print 'Invalid location'
			exit()

		res = self.br.submit()
		content = res.read()
		return content
	
	def getData(self,endmonth):
		f1 = open("newfile.txt", "w")
		f2 = open('newfileLWA.txt','w')
		year = 2015
		month = date.today().month
		timeZone = "6"
		for x in range(month,endmonth):
			for y in range(1,32):
				#Writes pages to storage file
				f1.write(self.getPage(str(month), str(y), str(year),timeZone,'TARA'))
				f2.write(self.getPage(str(month), str(y), str(year),timeZone,'LWA'))
			#Checks date
			if month < 12:
				month = month + 1
			elif month == 12:
				month = 1
				year = year + 1
			#Uncomment if timezone is not kept in database
			#if month == 11:
				#print "Time zone changed to 5"
				#timeZone = "5"

		f1.close()
		f2.close()

	def filterFiles(self):
		#opens the storage file, reads the contents
		f1 = open("newfile.txt", "r")
		#Filtered file to write data to
		f2 = open("TARA_Times.txt", "w")
		dates = []
		times = []

		f2.write("          Altitude    Azimuth    Fraction\n")
		f2.write("                      (E of N)  Illuminated\n")
		f2.write("              o           o                    \n")

		#Writes dates and filters entries
		temptimes = []
		dayprint = False
		for line in f1:
			#Splits the days
			#Uses year for consistancy
			if "2014" in line or "2015" in line:
				currdate = line
				dayprint = False
				if len(temptimes) > 0:
					times.append(temptimes)
					temptimes = []

			#Finds moon positions with ideal azimuth and zenith (250 degrees)
			if "251" in line or "250" in line:
				#Zenith is at least 45 degrees above horizon
				if float(line.split()[1]) > 45.0:
					if dayprint == False:
						f2.write(currdate)
						dates.append(currdate)
						dayprint = True
					else:
						f2.write(line)
						temptimes.append(line.split()[0])
						print line.split()[1]
				

		f1.close()
		f2.close()
		f3 = open("newfileLWA.txt", "r")
		f4 = open('LWA_Times.txt','w')
		i = -1
		j = 0
		for line in f3:
			if line == currdate:
				f4.write(line)
				i += 1
				j = 0
				if i > len(times):
					break
			elif times[i][j] in line and i >= 0 and j < len(times[i]):
				f4.write(line)
				j += 1

		f3.close()
		f4.close()

if __name__ == "__main__":
	mt = Moon_Times()
	#Get data from beginning of current month to end of
	#the month passed to the function (month = numeric month + 1)
	mt.getData(10)
	mt.filterFiles()
